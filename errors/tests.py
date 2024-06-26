from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse
from django.test import TestCase, RequestFactory
from unittest.mock import Mock
import os
from profiles.models import Profile, GuestProfile
from . import views
from yt_auth.models import Credentials


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
        self.anon_user = AnonymousUser()

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

    def test_error_handler_200(self):
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

    def test_error_handler_302(self):
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
        self.assertEqual(response.status_code, 404)
        # Guest
        response = Mock(status_code=404)
        request = self.guest_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 404)
        # Anonymous
        response = Mock(status_code=404)
        request = self.anon_request("/")
        response = views.error_handler(request, response)
        self.assertEqual(response.status_code, 404)

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

    def test_404_view(self):
        response = self.client.get("/404")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/asdfg")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/asdfg", follow=True)
        self.assertEqual(response.status_code, 404)
