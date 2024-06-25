from django.test import TestCase
import yt_auth.token_auth
from profiles.models import Profile, GuestProfile, make_user
from . import views
import google.oauth2.credentials as g_oa2_creds
from yt_auth.models import Credentials
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch, MagicMock, Mock
from django.contrib.sessions.backends import db
from django.urls import reverse
from django.test import TestCase, RequestFactory
from queues.models import Queue, has_authorization
from django.http import HttpResponseRedirect
import os
from django.test import RequestFactory
import yt_auth
from utils import check_valid_redirect_action

if os.path.isfile("env.py"):
    import env

LOCAL = eval(os.environ.get("LOCAL"))
if LOCAL:
    REDIRECT_URI = "http://localhost:8000/"
else:
    REDIRECT_URI = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/"

sample = "?state=BJn&code=4Eg&scope=https://www.googleapis.com/auth/youtube"


# Create your tests here.
class TestErrors(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_superuser(
            email="Testy@McTestFace.com",
            password="myPassword",
        )
        credentials = Credentials()
        credentials.save()
        self.user.credentials = credentials
        self.user.save()
        self.guest = GuestProfile(name="Guesty", email="Guesty@McTestFace.com")
        self.anon_user  = AnonymousUser()
    
    def user_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = self.user
        request.session = {}
        return request
    
    def anon_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request
    
    def guest_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {"guest_user": self.guest.serialize()}
        return request
    

    def _test_error_handler_200(self):
        # Logged in
        response = Mock(status_code=200)
        request = self.user_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        # Guest
        response = Mock(status_code=200)
        request = self.guest_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        # Anonymous
        response = Mock(status_code=200)
        request = self.anon_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        
    
    def _test_error_handler_302(self):
        # Logged in
        response = Mock(status_code=302)
        request = self.user_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)
        # Guest
        response = Mock(status_code=302)
        request = self.guest_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)
        # Anonymous
        response = Mock(status_code=302)
        request = self.anon_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)

    def test_error_handler_404(self):
        # Logged in
        response = Mock(status_code=404)
        request = self.user_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        test_string = str.encode("Page Not Found")
        self.assertContains(response, test_string)
        # Guest
        print("hit guest test")
        response = Mock(status_code=404)
        request = self.guest_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        test_string = str.encode("Page Not Found")
        self.assertContains(response, test_string)
        # Anonymous
        response = Mock(status_code=404)
        request = self.anon_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 200)
        test_string = str.encode("Page Not Found")
        self.assertContains(response, test_string)

    def test_error_handler_500(self):
        # Logged in
        response = Mock(status_code=500)
        request = self.user_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        # Guest
        response = Mock(status_code=500)
        request = self.guest_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("index"))
        # Anonymous
        response = Mock(status_code=500)
        request = self.anon_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("index"))