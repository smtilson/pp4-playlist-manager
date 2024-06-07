from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .oauth_permission_request import get_creds, get_creds_url
from .models import Profile
from .utils import empty_dict
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
    user = get_object_or_404(Profile, id=request.user.id)
    credentials = user.credentials
    context = {'user_id': user.id,
               "view_name": "test",
               'email': user.email,
               'credentials':credentials,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)
    
def test_function(request):
    """
    View to run test functions.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    url = get_creds_url()
    print(url)
    context = {'user_id': user.id,
               'view_name': "test_function",
               'email': user.email,
               'test_data':url,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)

def profile(request):
    """
    Test version of profile view, to load templates properly.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    credentials = user.credentials
    context = {'user_id': user.id,
               'email': user.email,
               "view_name":"profile",
               'credentials':credentials,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)

def remove_authorization(request):
    user = get_object_or_404(Profile, id=request.user.id)
    # there should be a modal for this
    user.remove_credentials()
    credentials = user.credentials
    msg = "credentials removed"
    context = {'user_id': user.id,
               'msg': msg,
               'email': user.email,
               "view_name":"remove_authorization",
               'test_data':user.test_char_field,
               'credentials': credentials,
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test.html", context)
    #return HttpResponseRedirect(reverse('test'))

def authorization(request):
    print('hit authorization view')
    user = get_object_or_404(Profile, id=request.user.id)
    credentials = user.credentials
    print(credentials)
    print(empty_dict(credentials))
    if not empty_dict(credentials):
        msg = "This user already has credentials"
        credentials['status']='old'
    else:
        credentials = get_creds()
        user.add_credentials(credentials)
        credentials = user.credentials
        credentials['status'] = 'new'
        msg = "new credentials fetched"
    context = {'user_id': user.id,
               'msg': msg,
               'email': user.email,
               "view_name":"authorization",
               'test_data':user.test_char_field,
               'credentials': credentials,
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test.html", context)

    