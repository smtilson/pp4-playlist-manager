from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from .models import Profile, GuestProfile, make_user
from utils import check_valid_redirect_action
from queues.models import Queue, has_authorization
from django.contrib import messages
from errors.models import RequestReport
from django.utils.safestring import mark_safe
from errors.views import error_handler, error_in_path
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    revoke_tokens,
)

# Create your views here.


def index(request):
    """
    Handles the index view for the app.
    Args: request (HttpRequest)
    Returns:
    """
    path = request.get_full_path()
    user = make_user(request)
    keywords = {"?state=", "&code=", "&scope=https://www.googleapis.com/auth/youtube"}
    valid_redirect = check_valid_redirect_action(request)
    request = error_in_path(request)
    if not valid_redirect:
        if not user.is_authenticated:
            response = render(request, "profiles/index.html")
        elif all(word in path for word in keywords):
            # should this be a redirect?
            response = return_from_authorization(request)
        else:
            response = HttpResponseRedirect(reverse("profile"))
    else:
        view_name = request.session["redirect_action"]["action"]
        args = request.session["redirect_action"]["args"]
        if has_authorization(user, args[0]) and len(args)==1:
            response = HttpResponseRedirect(reverse(view_name, args=args))
        else:
            msg = "Invalid redirect action encountered."
            messages.add_message(request, messages.INFO, msg)
            request.session["redirect_action"] = None
            response = HttpResponseRedirect(reverse("index"))
    response = error_handler(request, response)
    return response


def profile(request):
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
        if not user.has_tokens:
            youtube_permission_status = "Profile has no associated youtube account."
        else:
            youtube_permission_status = (
                f"Youtube DJ has access to {user.youtube_handle}."
            )
        info_dict = user.info_dict
        context = {
            "user": user,
            "view_name": "profile",
            "authorization_url": get_authorization_url(),
            "info_dict": info_dict,
            "my_queues": user.my_queues.all(),
            "other_queues": user.other_queues.all(),
            "youtube_access": youtube_permission_status,
        }
        response = render(request, "profiles/profile.html", context)
    """status, msg, msg_type = RequestReport.process(response)
    if status == 404:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("index"))"""
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
    user.name = request.POST["name"]
    user.save()
    msg = f"Name set to {user.name}"
    messages.add_message(request, messages.SUCCESS, msg)
    response = HttpResponseRedirect(reverse("profile"))
    """status, msg, msg_type = RequestReport.process(response)
    if status == 404:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))"""
    return response


def return_from_authorization(request):
    """
    Handles the redirect from Oauth2 authorization process.
    Args: request (HttpRequest)
    Returns: Redirects to appropriate page based on the outcome of the
    Oauth2 authorization process.
    """
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = make_user(request)
    if not user.is_authenticated:
        msg = "How did you get here, I am genuinely curious."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    else:
        path = request.get_full_path()
        if user.has_tokens:
            msg = f"{user.nickname} is already connected to {user.youtube_handle}. If you would like to change which account is connected, please first revoke the current permissions"
            msg_type = messages.INFO
        else:
            try:
                tokens = get_tokens(path)
            except Exception as e:
                msg = "An unknown error occurred while fetching your tokens."
                msg += str(e)
                msg_type = messages.ERROR
            else:
                msg = user.set_credentials(tokens)
                msg_type = messages.SUCCESS
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))
    """status, msg, msg_type = RequestReport.process(response)
    if status == 404:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))"""
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
    status_code = revoke_tokens(user)
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
    user.revoke_youtube_data()
    # there should be a modal for this
    messages.add_message(request, msg_type, mark_safe(msg))
    response = HttpResponseRedirect(reverse("profile"))
    """status, msg, msg_type = RequestReport.process(response)
    if status == 404:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))"""
    return response


def guest_sign_in(request):
    """
    Handles the guest sign-in process. Redirects user after sign in and
    generates a GuestProfile object.
    Args: request (HttpRequest)
    Returns:
    """
    queue = get_object_or_404(Queue, id=request.session["queue_id"])
    user = make_user(request)
    # are these ever hit? This seems maybe overly defensive.
    if user.is_authenticated:
        msg = "You are already logged in."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        if "redirect_action" in request.session:
            # The only usage of redirect_action is edit_queue.
            view_name = request.session["redirect_action"]["action"]
            args = request.session["redirect_action"]["args"]
            response = HttpResponseRedirect(reverse(view_name, args=args))
        else:
            response = HttpResponseRedirect(reverse("profile"))
    if request.method == "GET":
        context = {"queue": queue}
        return render(request, "profiles/guest_sign_in.html", context)
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
    """status, msg, msg_type = RequestReport.process(response)
    if status == 404:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("index"))"""
    return response
