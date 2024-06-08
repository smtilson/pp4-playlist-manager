from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .oauth_permission_request import get_creds, get_creds_url
from .models import Profile
from .utils import empty_dict, get_user_profile, get_data_from_path
from .google_oauth_from_docs import get_authorization_url, get_tokens
from yt_auth.models import Credentials
import json

# json1_file = open('json1')
# json1_str = json1_file.read()
# json1_data = json.loads(json1_str)
# json1_data = json.loads(json1_str)[0]


# Create your views here.


def index(request):
    path = request.get_full_path()
    if "code" in path:
        return return_from_authorization(request)
        return HttpResponseRedirect(reverse("after_auth"))
    else:
        return render(request, "profiles/index.html")


def auth_code(request):
    """
    Test view, to load templates properly.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    test_dict = {}
    test_dict["user_credentials"] = user.credentials
    test_dict["build_abs_uri"] = request.build_absolute_uri()
    test_dict["current_full_path"] = request.get_full_path()
    url, state0 = get_authorization_url()
    user.state0 = state0
    user.save()
    test_dict['state0'] = state0
    test_dict['state1'] = user.state1
    context = {
        "user_id": user.id,
        "view_name": "test",
        "email": user.email,
        "test_dict": test_dict,
        "test_data": url,
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)

def after_auth(request):
    user = get_object_or_404(Profile, id=request.user.id)
    test_dict = {}
    test_dict["user_credentials"] = user.credentials.to_dict()
    test_dict['state0'] = user.credentials.state0
    test_dict['state1'] = user.credentials.state1
    context = {
        "user_id": user.id,
        "view_name": "test",
        "email": user.email,
        "test_dict": test_dict,
        "test_data": '',
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)


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
        "test_data": '',
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)


def test_function(request):
    """
    View to run test functions.
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
        "test_data": '',
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)


def profile(request):
    """
    Test version of profile view, to load templates properly.
    This can be cleaned up still.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    if user.credentials is None:
        has_tokens = False
    else:
        has_tokens = user.credentials.has_tokens
    if not has_tokens:
        url = get_authorization_url()
    else:
        url='#'
    context = {
        "user_id": user.id,
        "email": user.email,
        "view_name": "profile",
        "has_tokens":has_tokens,
        "test_data": '',
        "authorization_url": url,
        "youtube_account": "none as of yet",
    }
    if has_tokens:
        context['test_dict']=user.credentials.to_dict()
    return render(request, "profiles/test.html", context)


def remove_authorization(request):
    user = get_object_or_404(Profile, id=request.user.id)
    # there should be a modal for this
    user.remove_credentials()
    credentials = user.credentials
    msg = "credentials removed"
    context = {
        "user_id": user.id,
        "msg": msg,
        "email": user.email,
        "view_name": "remove_authorization",
        "test_data": user.test_char_field,
        "test_dict": credentials,
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)
    # return HttpResponseRedirect(reverse('test'))


def return_from_authorization(request):
    # do I need to check here that they don't have credentials since it is checked on the front end
    user = get_user_profile(request)
    path = request.get_full_path()
    tokens = get_tokens(path).to_json()
    user,credentials = Credentials.from_json(tokens)
    user.save()
    return HttpResponseRedirect(reverse("after_auth"))
    user.add_credentials(credentials)
    credentials = user.credentials
    credentials["status"] = "new"
    msg = "new credentials fetched"
    context = {
        "user_id": user.id,
        "msg": msg,
        "email": user.email,
        "view_name": "authorization",
        "test_data": user.test_char_field,
        "test_dict": credentials,
        "youtube_account": "none as of yet",
    }
    return render(request, "profiles/test.html", context)
