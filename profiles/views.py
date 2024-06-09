from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Profile
from yt_auth.token_auth import (
    get_authorization_url,
    get_tokens,
    revoke_tokens,
    refresh_tokens,
)
from yt_auth.models import Credentials

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
    user = get_object_or_404(Profile, id=request.user.id)
    test_dict = {}
    test_dict["user_credentials"] = user.credentials
    test_dict["build_abs_uri"] = request.build_absolute_uri()
    test_dict["current_full_path"] = request.get_full_path()
    context = {
        "user_id": user.id,
        "view_name": "test",
        "email": user.email,
        "test_dict": test_dict,
        "test_data": "",
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)


def test_function(request):
    """
    View to run test functions.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    # this should not in general be necessary
    '''if user.credentials is None:
        empty_creds = Credentials()
        empty_creds.save()
        user.credentials = empty_creds
        user.save()'''
    if not user.has_tokens:
        url = get_authorization_url()
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
    user = get_object_or_404(Profile, id=request.user.id)
    # this should not in general be necessary
    '''if user.credentials is None:
        empty_creds = Credentials()
        empty_creds.save()
        user.credentials = empty_creds
        user.save()'''
    if not user.has_tokens:
        url = get_authorization_url()
        msg = "Profile has no associated youtube account."
    else:
        url = "#"
        msg = "Youtube DJ has access to your youtube account."
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
    test_dict['valid'] = user.valid_credentials
    context["test_dict"] = test_dict

    return render(request, "profiles/test.html", context)


def remove_authorization(request):
    user = get_object_or_404(Profile, id=request.user.id)
    # there should be a modal for this
    user.set_credentials()
    # revoke_tokens(request)
    return HttpResponseRedirect(reverse("profile"))
    # return HttpResponseRedirect(reverse('test'))


def return_from_authorization(request):
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = Profile.get_user_profile(request)
    path = request.get_full_path()
    tokens = get_tokens(path)
    print(tokens)
    user.set_credentials(tokens)
    user.save()
    return HttpResponseRedirect(reverse("profile"))
