from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .oauth_permission_request import get_creds
from .models import Profile
from .utils import get_user_profile


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
               'youtube_account': 'none as of yet' }
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

def authorization(request):
    user = get_user_profile(request)
    credentials = get_creds()
    #credentials = {i:i+1 for i in range(5)}
    print(type(credentials))
    input()
    user.add_credentials(credentials)
    context = {'user_id': user.id,
               'email': user.email,
               'credentials':credentials,
               "str_creds":str(credentials),
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test.html", context)

    