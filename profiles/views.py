from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.contrib import messages
from requests.exceptions import HTTPError
from typing import Optional, Union, Callable, Literal
from functools import wraps
from .models import GuestProfile, make_user, Profile
from utils import check_valid_redirect_action, with_error_handling, require_auth
from queues.models import Queue, has_authorization
from errors.utils import process_path
from errors.views import error_handler
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    revoke_tokens,
)

# TODO: Add type hints to all view functions. This is a bit tricky because of the way the auth_user is passed in, but it should be doable with some careful thought.

@with_error_handling
def index(request):
    """
    Handles the index view for the app. Redirects user based on authentication
    status, session data, and path.
    Args: request (HttpRequest)
    Returns: Various HttpResponseRedirects and renders the appropriate page.
    """
    path = request.get_full_path()
    user = make_user(request)
    keywords = {"?state=", "&code=", "&scope=https://www.googleapis.com/auth/youtube"}
    queue_id = getattr(user, "queue_id", False)
    if all(word in path for word in keywords):
        # TODO(sean+copilot): Preserve OAuth query params when redirecting and
        # finish wiring callback handling so return_from_authorization receives
        # state/code directly without view-to-view call side effects.
        return HttpResponseRedirect(reverse("return_from_authorization"))  # type: ignore[return-value]
    elif "error" in path:
        msg = "An error occurred during the previous process."
        msg += process_path(path)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse("profile"))
    elif check_valid_redirect_action(request):
        return HttpResponseRedirect(reverse("redirect_action"))
    elif user.is_guest and queue_id:
        return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    else:
        return render(request, "profiles/index.html")

@with_error_handling
@require_auth("You must be logged in to view your profile.")
def profile(request, *args, auth_user: Profile, **kwargs):
    """
    Renders the profile page for a user.
    Args: request (HttpRequest)
    Returns: Redirects to the "login" page if the user is not authenticated,
        otherwise renders the appropriate "profile" page.
    """
    if not auth_user.credentials:
        auth_user.initialize()
    if auth_user.youtube_handle:
        youtube_permission_status = (
            f"Youtube DJ has access to {auth_user.youtube_handle}."
        )
    else:
        youtube_permission_status = "Profile has no associated youtube" "account."
    context = {
        "user": auth_user,
        "authorization_url": get_authorization_url(),
        "info_dict": auth_user.info_dict,
        "my_queues": auth_user.my_queues.all(),
        "other_queues": auth_user.other_queues.all(),
        "youtube_access": youtube_permission_status,
    }
    return render(request, "profiles/profile.html", context)

@with_error_handling
@require_auth("You must be logged in to set your name.")
@require_POST
def set_name(request, *args, auth_user: Profile, **kwargs):
    """
    Sets the name of the user based on their input.
    Args: request (HttpRequest)
    Returns: Redirects to the "profile" page if the name is successfully set.
    Redirects to the "account_login" page if the user is not authenticated.
    """
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Name cannot be empty.")
        return HttpResponseRedirect(reverse("profile"))

    auth_user.name = name
    auth_user.save()
    messages.success(request, f"Name set to {auth_user.name}")
    return HttpResponseRedirect(reverse("profile"))
    
confused_msg = (
        "How did you get here? I am genuinely curious. This"
        " authorization code will be discarded and you will have to try"
        " again after you are logged in."
    )
@with_error_handling
@require_auth(confused_msg)
def return_from_authorization(request, *args, auth_user: Profile, **kwargs):
    """
    Handles the redirect from Oauth2 authorization process.
    Args: request (HttpRequest)
    Returns: Redirects to appropriate page based on the outcome of the
    Oauth2 authorization process.
    """
    path = request.get_full_path()
    try:
        tokens = get_tokens(path)
        msg = auth_user.set_credentials(tokens)
        auth_user.save()
        messages.success(request, msg)
    except HTTPError as e:
        error_msg = "An unknown error occurred while fetching your tokens."
        error_msg += str(e)
        error_msg += "error occurred while retrieving tokens"
        messages.error(request, error_msg)
    return HttpResponseRedirect(reverse("profile"))
    

@with_error_handling
@require_auth("You must be logged in to revoke your authorization.")
def revoke_authorization(request, *args, auth_user: Profile, **kwargs):
    """
    Invalidates google credentials and clears them from the database. In case
    of an error, a link to revoke the user's permissions on the Google account
    Args: request (HttpRequest)
    Returns: Redirect to the "profile" page.
    """
    # This error code is never 200, but sometimes the credentials are
    # invalidated on Google's end as well.
    status_code = revoke_tokens(auth_user)
    auth_user.revoke_youtube_data()
    if status_code == 200:
        messages.success(request, f"Credentials successfully revoked for {auth_user.youtube_handle}")
    else:
        address = (
            '<a href="https://myaccount.google.com/permissions">"'
            "Third party apps and services</a>"
        )
        messages.error(request, mark_safe(
            "An error occurred. Your credentials have been wiped from"
            " our system. To be on the safe side, please visit"
            f" {address} to revoke your permissions. Look for "
            "'pp4-playlist-manager' in the list of third party apps."
        ))
    return HttpResponseRedirect(reverse("profile"))
    

@with_error_handling
def redirect_action(request):
    """
    Redirects the user to a specific view based on the session data. Currently,
    only one redirect action is implemented.
    Args: request (HttpRequest)
    Returns: Redirect to Edit page for the given queue, if the user has
    authorization.
    """
    # Currently, only one redirect action is implemented
    user = make_user(request)
    if not check_valid_redirect_action(request):
        messages.error(request, "An error occurred. There is no valid redirect action.")
        return HttpResponseRedirect(reverse("index"))
    view_name = request.session.pop("redirect_action", None)
    queue_id = request.session.pop("queue_id", None)
    if not view_name or not queue_id:
        messages.error(request, "An error occurred. There is no redirect target action.")
        return HttpResponseRedirect(reverse("index"))
    if not has_authorization(user, queue_id):
        messages.error(request, "An error occurred. You are not authorized to access this page.")
        return HttpResponseRedirect(reverse("index"))    
    messages.success(request, "Redirecting to Edit page for the given queue.")
    return HttpResponseRedirect(reverse(view_name, args=[queue_id]))

@with_error_handling
def guest_sign_in(request):
    """
    Handles the guest sign-in process. Redirects user after sign in and
    generates a GuestProfile object and stores it in the session.
    Args: request (HttpRequest)
    Returns:
    """
    user = make_user(request)
    queue_id = request.session.get("queue_id")
    if queue_id is None:
        raise Http404("A queue must be associated with this particular request.")
    queue = get_object_or_404(Queue, id=queue_id)
    # I don't understand this or statement.
    if user.is_authenticated or user.is_guest:
        messages.info(request, f"You are already logged in {user.nickname}.")
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    elif request.method == "GET":
        context = {"queue": queue}
        response = render(request, "profiles/guest_sign_in.html", context)
    elif request.method == "POST":
        name = request.POST.get("guest_name", "").strip()
        if not name:
            messages.error(request, "Guest name cannot be empty.")
            return HttpResponseRedirect(reverse("guest_sign_in"))
        email = request.POST.get("guest_email")
        user = GuestProfile(
            name=name,
            email=email,
            queue_id=queue.pk,
            queue_secret=queue.secret,
            owner_secret=queue.owner.secret,
        )
        request.session["guest_user"] = user.serialize()
        messages.success(request, f"Guest account set up for {user.nickname}")
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue.pk]))
    else:
        response = HttpResponseRedirect(reverse("index"))
    
    return response


# this should be a delete http method, not a get or a post.
# check the status codes that are being returned
@with_error_handling
@require_auth("You must be logged in to delete your account.")
def delete_profile(request, *args, auth_user: Profile, **kwargs):
    """
    Handles the account deletion process. Removes user data from the session
    and revokes YouTube API credentials.
    Args: request (HttpRequest)
    Returns: Redirects to the index page with a success message.
    """
    # TODO: This should be changed to delete http method, but that seems to require a JS api call.
    if request.method not in {"POST", "DELETE"}:
        messages.error(request, "Invalid request method. Please use POST or DELETE to delete your account.")
        return HttpResponseRedirect(reverse("profile"))
    try:
        # Revoke YouTube API credentials
        revoke_tokens(auth_user)
    except HTTPError as e:
        error_msg = "An unknown error occurred while revoking your credentials."
        error_msg += str(e)
        messages.error(request, error_msg)
        # Remove user data from the database
    auth_user.delete()  # type: ignore [attr-defined]
    # TODO: Logout user from session?
    messages.success(request, "Your account has been deleted.")
    return HttpResponseRedirect(reverse("account_signup"))

