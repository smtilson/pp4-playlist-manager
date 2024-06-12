from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Profile, GuestProfile
from queues.models import Queue
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    save_creds,
    revoke_tokens,
)
from yt_auth.models import Credentials
from django.utils.crypto import get_random_string

# Create your views here.


def index(request):
    path = request.get_full_path()
    if "code" in path:
        # should this be a redirect?
        return return_from_authorization(request)
    else:
        return render(request, "profiles/index.html")


def test(request):
    """
    Test view, to load templates properly.
    """
    user = request.user
    test_dict = {"request_user_dir": request.user.__dir__()}
    context = {
        "user_id": user.id,
        "view_name": "test",
        "email": user.email,
        "test_dict": test_dict,
        "test_data": "",
        "youtube_account": "none as of yet",
    }
    request.data_tag1234 = "testing"
    return render(request, "profiles/test.html", context)


def test_function(request):
    """
    View to run test functions.
    """
    user = request.user
    # this should not in general be necessary

    if user.credentials is None:
        empty_creds = Credentials()
        empty_creds.save()
        user.credentials = empty_creds
        user.save()
    else:
        url = "#"
    context = {
        "user_id": user.id,
        "email": user.email,
        "view_name": "profile",
        "has_tokens": user.has_tokens,
        "test_data": "",
        "authorization_url": url,
        "youtube_account": "none as of yet",
    }
    test_dict = user.credentials.to_dict()
    test_dict["msg"] = msg
    context["test_dict"] = test_dict

    return render(request, "profiles/test.html", context)


def profile(request):
    """
    Test version of profile view, to load templates properly.
    This can be cleaned up still.
    """
    user = request.user
    print(user.to_dict())
    # if not user.secret:
    #    user.initialize()
    url = get_authorization_url()
    if not user.credentials:
        user.initialize()
    if not user.has_tokens:
        msg = "Profile has no associated youtube account."
    else:
        msg = "Youtube DJ has access to your youtube account."
    context = {
        "user": user,
        "view_name": "profile",
        "authorization_url": url,
    }
    # test_dict = user.credentials.to_dict()
    test_dict = user.to_dict()
    test_dict["msg"] = msg
    test_dict["valid"] = user.valid_credentials
    context["test_dict"] = test_dict
    context["my_queues"] = user.my_queues.all()
    context["other_queues"] = user.other_queues.all()

    return render(request, "profiles/profile.html", context)


def revoke_authorization(request):
    user = request.user
    msg = revoke_tokens(request)
    print(msg)
    # there should be a modal for this
    user.revoke_youtube_data()
    # revoke_tokens(request)
    return HttpResponseRedirect(reverse("profile"))
    # return HttpResponseRedirect(reverse('test'))


def return_from_authorization(request):
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = request.user
    path = request.get_full_path()
    tokens = get_tokens(path)
    save_creds(tokens)
    print(tokens)
    user.set_credentials(tokens)
    return HttpResponseRedirect(reverse("profile"))


def guest_sign_in(request):
    if request.method == "GET":
        return render(request, "profiles/guest_sign_in.html")
    elif request.method == "POST":
        name = request.POST["guest_name"]
        email = request.POST.get("guest_email", "")
        user = GuestProfile(
            name=name,
            email=email,
            queue_id=request.session["queue_id"],
            queue_secret=request.session["queue_secret"],
            owner_secret=request.session["owner_secret"],
        )
        request.session["guest_user"]=user.serialize()
        return HttpResponseRedirect(
            reverse("edit_queue", args=[request.session["queue_id"]])
        )
