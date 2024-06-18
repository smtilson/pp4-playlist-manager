from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from .models import Profile, GuestProfile, make_user
from queues.models import Queue
from django.contrib import messages
from errors.models import RequestReport
from django.utils.safestring import mark_safe
from error_processing import process_path
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    revoke_tokens,
)
from yt_auth.models import Credentials

# Create your views here.


def index(request):
    """
    Handles the index view for the app.
    Args: request (HttpRequest)
    Returns:
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    path = request.get_full_path()
    print(path)
    user = make_user(request)
    if "code" in path:
        # should this be a redirect?
        return return_from_authorization(request)
    elif "error" in path:
        error_msg = process_path(path)
        print(error_msg)
        messages.add_message(request, messages.ERROR, error_msg)
        if user.is_authenticated:
            return HttpResponseRedirect(reverse("profile"))
        return render(
            request, "profiles/index.html", {"error_msg": error_msg, "user": user}
        )
    elif "redirect_action" in request.session:
        view_name = request.session["redirect_action"]["action"]
        args = request.session["redirect_action"]["args"]
        return HttpResponseRedirect(reverse(view_name, args=args))
    elif user.is_authenticated:
        return HttpResponseRedirect(reverse("profile"))
    else:
        return render(request, "profiles/index.html", {"user": user})


def profile(request):
    """
    Renders the profile page for a user.
    Args: request (HttpRequest)
    Returns: Redirects to the "login" page if the user is not authenticated,
        otherwise renders the appropriate "profile" page.
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to view your profile."
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse("account_login"))
    if not user.credentials:
        user.initialize()
    if not user.has_tokens:
        youtube_permission_status = "Profile has no associated youtube account."
    else:
        youtube_permission_status = "Youtube DJ has access to your youtube account."
    info_dict = user.info_dict
    info_dict["Youtube Access"] = youtube_permission_status
    info_dict["Are Credentials Valid?"] = user.valid_credentials
    context = {
        "user": user,
        "view_name": "profile",
        "authorization_url": get_authorization_url(),
        "info_dict": info_dict,
        "my_queues": user.my_queues.all(),
        "other_queues": user.other_queues.all(),
    }
    return render(request, "profiles/profile.html", context)


def set_name(request):
    """
    Sets the name of the user based on their input.
    Args: request (HttpRequest)
    Returns: Redirects to the "profile" page if the name is successfully set.
    Redirects to the "account_login" page if the user is not authenticated.
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to set your name."
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse("account_login"))
    user.name = request.POST["name"]
    user.save()
    msg = f"Name set to {user.name}"
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("profile"))


def revoke_authorization(request):
    """
    Invalidates google credentials and clears them from the database. In case
    of an error, a link to revoke the user's permissions on the Google account
    Args: request (HttpRequest)

    Returns: Redirect to the "profile" page.
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to revoke your authorization."
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse("account_login"))
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
    return HttpResponseRedirect(reverse("profile"))


def return_from_authorization(request):
    """
    Handles the redirect from Oauth2 authorization process.
    Args: request (HttpRequest)
    Returns: Redirects to appropriate page based on the outcome of the
    Oauth2 authorization process.
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = make_user(request)
    if not user.is_authenticated:
        msg = "How did you get here, I am genuinely curious."
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse("account_login"))
    path = request.get_full_path()
    if user.has_tokens:
        msg = f"{user.nickname} is already connected to {user.youtube_handle}. If you would like to change which account is connected, please first revoke the current permissions"
        msg_type = messages.INFO
    else:
        tokens = get_tokens(path)
        msg = user.set_credentials(tokens)
        msg_type = messages.SUCCESS
    messages.add_message(request, msg_type, msg)
    return HttpResponseRedirect(reverse("profile"))


def guest_sign_in(request):
    """
    Handles the guest sign-in process.

    Args: request (HttpRequest)

    Returns:
    """
    success, msg, msg_type = RequestReport.process(request)
    if not success:
        messages.add_message(request, msg_type, msg)
        return HttpResponseRedirect(reverse("404"))
    queue = get_object_or_404(Queue, id=request.session["queue_id"])
    user = make_user(request)
    # are these ever hit? This seems maybe overly defensive.
    if user.is_authenticated:
        msg = "You are already logged in."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        if "redirect_action" in request.session:
            view_name = request.session["redirect_action"]["action"]
            args = request.session["redirect_action"]["args"]
            return HttpResponseRedirect(reverse(view_name, args=args))
        else:
            return HttpResponseRedirect(reverse("profile"))
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
        return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
