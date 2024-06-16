from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from .models import Profile, GuestProfile, make_user
from queues.models import Queue
from django.contrib import messages
from error_processing import process_path
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    save_creds,
    revoke_tokens,
)
from yt_auth.models import Credentials

# Create your views here.


def index(request):
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
        return render(request, "profiles/index.html", {"error_msg": error_msg})
    elif "redirect_action" in request.session:
        view_name = request.session["redirect_action"]["action"]
        args = request.session["redirect_action"]["args"]
        return HttpResponseRedirect(reverse(view_name, args=args))
    elif user.is_authenticated:
        return HttpResponseRedirect(reverse("profile"))
    else:
        return render(request, "profiles/index.html")


def profile(request):
    """
    Test version of profile view, to load templates properly.
    This can be cleaned up still.
    """
    user = make_user(request)
    if user.is_guest or not user.is_authenticated:
        return HttpResponseRedirect(reverse("account_signup"))
    if not getattr(user,"credentials"):
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

def test(request):
    return JsonResponse({"test":"test"})

def set_name(request):
    user = make_user(request)
    user.name = request.POST["name"]
    user.save()
    msg = f"Name set to {user.name}"
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("profile"))


def revoke_authorization(request):
    user = make_user(request)
    msg = revoke_tokens(user)
    print(msg)
    # there should be a modal for this
    user.revoke_youtube_data()
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("profile"))
    # return HttpResponseRedirect(reverse('test'))


def return_from_authorization(request):
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = request.user
    path = request.get_full_path()
    if user.has_tokens:
        msg = f"{user.nickname} is already connected to {user.youtube_handle}. If you would like to change which account is connected, please first revoke the current permissions"
    tokens = get_tokens(path)
    #save_creds(tokens)
    #print(tokens)
    # set_credentials saves them
    msg = user.set_credentials(tokens)
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("profile"))


def guest_sign_in(request):
    if request.method == "GET":
        return render(request, "profiles/guest_sign_in.html")
    elif request.method == "POST":
        name = request.POST["guest_name"]
        email = request.POST.get("guest_email")
        user = GuestProfile(
            name=name,
            email=email,
            queue_id=request.session["queue_id"],
            queue_secret=request.session["queue_secret"],
            owner_secret=request.session["owner_secret"],
        )
        request.session["guest_user"] = user.serialize()
        msg = f"Guest account set up for {user.nickname}"
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(
            reverse("edit_queue", args=[request.session["queue_id"]])
        )
