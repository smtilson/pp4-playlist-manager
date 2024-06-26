from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, Http404
from .models import Profile, GuestProfile, make_user
from utils import check_valid_redirect_action
from queues.models import Queue, has_authorization
from django.contrib import messages
from errors.utils import process_path
from django.utils.safestring import mark_safe
from errors.views import error_handler
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    revoke_tokens,
)

# Create your views here.


def index(request):
    # need to test guest without redirect
    """
    Handles the index view for the app.
    Args: request (HttpRequest)
    Returns:
    """
    path = request.get_full_path()
    print(path)
    user = make_user(request)
    keywords = {"?state=", "&code=", "&scope=https://www.googleapis.com/auth/youtube"}
    if all(word in path for word in keywords):
        response = return_from_authorization(request)
    elif "error" in path:
        msg = "An error occurred during the previous process."
        msg += process_path(path)
        messages.add_message(request, messages.ERROR, msg)
        response = HttpResponseRedirect(reverse("profile"))
    elif check_valid_redirect_action(request):
        response = HttpResponseRedirect(reverse("redirect_action"))
    elif user.is_guest and user.queue_id:
        response = HttpResponseRedirect(reverse("edit_queue", args=[user.queue_id]))
    else:
        response = render(request, "profiles/index.html")
    response = error_handler(request, response)
    return response


def profile(request):
    # finished testing
    """
    Renders the profile page for a user.
    Args: request (HttpRequest)
    Returns: Redirects to the "login" page if the user is not authenticated,
        otherwise renders the appropriate "profile" page.
    """
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to view your profile."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    else:
        if not user.credentials:
            user.initialize()
        if user.youtube_handle:
            youtube_permission_status = (
                f"Youtube DJ has access to {user.youtube_handle}."
            )
        else:
            youtube_permission_status = "Profile has no associated youtube account."
        context = {
            "user": user,
            "authorization_url": get_authorization_url(),
            "info_dict": user.info_dict,
            "my_queues": user.my_queues.all(),
            "other_queues": user.other_queues.all(),
            "youtube_access": youtube_permission_status,
        }
        response = render(request, "profiles/profile.html", context)
    response = error_handler(request, response)
    return response


def set_name(request):
    """
    Sets the name of the user based on their input.
    Args: request (HttpRequest)
    Returns: Redirects to the "profile" page if the name is successfully set.
    Redirects to the "account_login" page if the user is not authenticated.
    """
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to set your name."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    elif request.method != "POST":
        msg = "Invalid request method."
        messages.add_message(request, messages.INFO, msg)
    else:
        user.name = request.POST["name"]
        user.save()
        msg = f"Name set to {user.name}"
        messages.add_message(request, messages.SUCCESS, msg)
    response = HttpResponseRedirect(reverse("profile"))
    response = error_handler(request, response)
    return response


def return_from_authorization(request):
    # not finished testing
    """
    Handles the redirect from Oauth2 authorization process.
    Args: request (HttpRequest)
    Returns: Redirects to appropriate page based on the outcome of the
    Oauth2 authorization process.
    """
    # do I need to check here that they don't have credentials since it is checked on the front end
    # no, but I do need to overwrite the credentials they do have since requesting new ones invalidates the current ones, I believe.
    user = make_user(request)
    if not user.is_authenticated:
        msg = "How did you get here? I am genuinely curious."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    else:
        path = request.get_full_path()
        print(path)
        try:
            tokens = get_tokens(path)
        # something should be done about this exceptioin
        except Exception as e:
            print("error occurred while retrieving tokens")
            msg = "An unknown error occurred while fetching your tokens."
            msg += str(e)
            msg += "error occurred while retrieving tokens"
            # print(e)
            msg_type = messages.ERROR
        else:
            msg = user.set_credentials(tokens)
            user.save()
            msg_type = messages.SUCCESS
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))
    response = error_handler(request, response)
    return response


def revoke_authorization(request):
    """
    Invalidates google credentials and clears them from the database. In case
    of an error, a link to revoke the user's permissions on the Google account
    Args: request (HttpRequest)
    Returns: Redirect to the "profile" page.
    """
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to revoke your authorization."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    else:
        # This error code is never 200, but sometimes the credentials are
        # invalidated on Google's end as well.
        status_code = revoke_tokens(user)
        user.revoke_youtube_data()
        if status_code == 200:
            msg = "Credentials successfully revoked for " + user.youtube_handle
            msg_type = messages.SUCCESS
        else:
            address = '<a href="https://myaccount.google.com/permissions">Third party apps and services</a>'
            msg = "An error occurred. Your credentials have been wiped from our "
            msg += f"system. To be on the safe side, please visit {address}"
            msg += "to revoke your permissions. Look for 'pp4-playlist-manager' in"
            msg += "the list of third party apps."
            msg_type = messages.ERROR
        # there should be a modal for this
        messages.add_message(request, msg_type, mark_safe(msg))
        response = HttpResponseRedirect(reverse("profile"))
    response = error_handler(request, response)
    return response


def redirect_action(request):
    # finished testing
    # Currently only one redirect action is implemented
    user = make_user(request)
    if check_valid_redirect_action(request):
        view_name = request.session["redirect_action"]
        del request.session["redirect_action"]
        queue_id = request.session["queue_id"]
    if has_authorization(user, queue_id):
        msg = "Redirecting to Edit page for the given queue."
        msg_type = messages.SUCCESS
        response = HttpResponseRedirect(reverse(view_name, args=[queue_id]))
    else:
        msg = "An error occurred. There is no valid redirect action."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("index"))
    messages.add_message(request, msg_type, msg)
    response = error_handler(request, response)
    return response


def guest_sign_in(request):
    # finished testing
    """
    Handles the guest sign-in process. Redirects user after sign in and
    generates a GuestProfile object.
    Args: request (HttpRequest)
    Returns:
    """
    user = make_user(request)
    queue_id = request.session.get("queue_id")
    if queue_id is None:
        raise Http404("A queue must be associated with this particular request.")
    else:
        queue = get_object_or_404(Queue, id=request.session["queue_id"])
    if user.is_authenticated or user.is_guest:
        msg = f"You are already logged in {user.nickname}."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    elif request.method == "GET":
        context = {"queue": queue}
        response = render(request, "profiles/guest_sign_in.html", context)
    elif request.method == "POST":
        name = request.POST["guest_name"]
        email = request.POST.get("guest_email")
        user = GuestProfile(
            name=name,
            email=email,
            queue_id=queue.id,
            queue_secret=queue.secret,
            owner_secret=queue.owner.secret,
        )
        request.session["guest_user"] = user.serialize()
        msg = f"Guest account set up for {user.nickname}"
        messages.add_message(request, messages.SUCCESS, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    else:
        response = HttpResponseRedirect(reverse("index"))
    response = error_handler(request, response)
    return response
