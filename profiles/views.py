from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .oauth_permission_request import get_creds, get_creds_url
from .models import Profile
from .utils import empty_dict
from .google_oauth_from_docs import get_authorization_url
import json

#json1_file = open('json1')
#json1_str = json1_file.read()
#json1_data = json.loads(json1_str)
#json1_data = json.loads(json1_str)[0]


# Create your views here.

def index(request):
    if request.method == "GET":
        return render(request, "profiles/index.html")
    elif request.method == "POST":
        print(request.__dir_())
        credentials = {key: value for key,value in request.items()}
        context = {'user_id': user.id,
               "view_name": "test",
               'email': user.email,
               'test_dict':credentials,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)
        

def auth_code(request):
    """
    Test view, to load templates properly.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    test_dict = {}
    test_dict['user_credentials']= user.credentials
    test_dict['build_abs_uri']=request.build_absolute_uri()
    test_dict['current_full_path']=request.get_full_path()
    context = {'user_id': user.id,
               "view_name": "test",
               'email': user.email,
               'test_dict':test_dict,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)

def test(request):
    """
    Test view, to load templates properly.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    credentials = user.credentials
    context = {'user_id': user.id,
               "view_name": "test",
               'email': user.email,
               'test_dict':credentials,
               'test_data':user.test_char_field,
               'youtube_account': 'none as of yet'}
    return render(request, "profiles/test.html", context)
    
def test_function(request):
    """
    View to run test functions.
    """
    user = get_object_or_404(Profile, id=request.user.id)
    url = get_authorization_url()
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
               'test_dict':credentials,
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
               'test_dict': credentials,
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
               'test_dict': credentials,
               'youtube_account': 'none as of yet' }
    return render(request, "profiles/test.html", context)

    