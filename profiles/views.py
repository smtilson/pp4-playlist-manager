from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .oauth_permission_request import check_creds


# Create your views here.
def test(request):
    """
    Test view, to load templates properly.
    """
    
    return render(request, "profiles/index.html")

def profile(request, user_id):
    context = {'user_id': user_id,
               'email': request.user.email,
                'youtube_account': 'none as of yet' }
    return render(request, "profiles/profile.html", context)

def authorization(request, user_id):
    print('authorization view hit')
    check_creds()
    return HttpResponseRedirect(reverse('profile', args=[user_id]))