from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .oauth_permission_request import get_creds
from .models import Profile
from .utils import get_user_profile
import json

#json1_file = open('json1')
#json1_str = json1_file.read()
#json1_data = json.loads(json1_str)
#json1_data = json.loads(json1_str)[0]
# Create your views here.

def index(request):
    return render(request, "profiles/index.html")

def test(request):
    """
    Test view, to load templates properly.
    """
    user = get_user_profile(request)
    credentials = user.get_credentials()
    context = {'user_id': user.id,
               'email': user.email,
               'credentials':credentials,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)

def profile(request, user_id):
    context = {'user_id': user_id,
               'email': request.user.email,
               'is_superuser':request.user.is_superuser,
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/profile.html", context)

def do_test_modify_profile(request):
    user = get_user_profile(request)
    old = user.test_char_field
    print(old)
    user.save_test_modify()
    print(user.test_char_field)
    context = {'user_id': user.id,
               'email': user.email,
               'is_superuser':user.is_superuser,
               'old':old,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test_modify_profile.html", context)

def credentials(request):
    return index(request)

def save_creds(request):
    user = get_object_or_404(Profile,id=request.user.id)
    
    user.add_credentials()

def authorization(request):
    user = get_object_or_404(Profile, id=request.user.id)
    credentials = get_creds()
    print(credentials)
    print(type(credentials))
    user.add_credentials(credentials)
    context = {'user_id': user.id,
               'email': user.email,
               'credentials':credentials,
               "str_creds":str(credentials),
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test.html", context)

    