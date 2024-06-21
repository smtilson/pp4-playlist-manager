from .models import Profile, GuestProfile, make_user
from . import views
from yt_auth.models import Credentials
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch
from django.contrib.sessions.backends import db
from django.urls import reverse
from django.test import TestCase, RequestFactory
from queues.models import Queue
from django.http import HttpResponseRedirect
import os

if os.path.isfile("env.py"):
    import env

LOCAL = eval(os.environ.get("LOCAL"))
if LOCAL:
    REDIRECT_URI = "http://localhost:8000/"
else:
    REDIRECT_URI = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/"


class TestProfileViews(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = Profile.objects.create_superuser(
            email="Testy1@McTestFace.com",
            password="myPassword",
        )
        credentials1 = Credentials()
        credentials1.save()
        self.user1.credentials = credentials1
        self.user1.save()
        self.user2 = Profile.objects.create_superuser(
            email="Testy2@McTestFace.com",
            password="myPassword",
        )
        credentials2 = Credentials()
        credentials2.save()
        self.user2.credentials = credentials2
        self.user2.save()

        self.queue1 = Queue(
            owner=self.user1,
            title="Test Queue1 Title",
            description="Test Queue1 Description",
            kind="",
            yt_id="",
        )
        self.queue2 = Queue(
            owner=self.user2,
            title="Test Queue2 Title",
            description="Test Queue2 Description",
            kind="",
            yt_id="",
        )
        self.queue1.save()
        self.queue2.save()
        self.guest = GuestProfile(name="Guesty", email="Guesty@McTestFace.com")
        self.guest.queue_id = self.queue1.id

    def setup_session(self, path, session: dict = {}):
        request = self.factory.get(path)
        request.session = session
        return request

    def _test_make_user(self):
        # Anonymous User
        request = self.setup_session("/")
        request.user = AnonymousUser()
        user = make_user(request)
        self.assertFalse(user.is_authenticated)
        self.assertFalse(user.is_guest)
        # Guest User
        session = {"guest_user": self.guest.serialize()}
        request = self.setup_session("/", session)
        request.user = AnonymousUser()
        user = make_user(request)
        self.assertFalse(user.is_authenticated)
        self.assertTrue(user.is_guest)
        # Logged in User
        request = self.setup_session("/")
        request.user = self.user1
        user = make_user(request)
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_guest)

    def test_index_not_logged_in(self):
        # Base Case
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        



    def test_index_not_logged_in_redirect_action(self):
        # Guest with good session data
        session = {
            "guest_user": self.guest.serialize(),
                "redirect_action": {
                    "action": "edit_queue", 
                    "args": [self.queue2.id]
                    }
                }
        request = self.setup_session("/", session)
        request.user = AnonymousUser()
        response = views.index(request)
        print(response.status_code)
        self.assertEqual(response.status_code,302)
        path = response.headers["Location"]
        self.assertEqual(path, '/queues/edit_queue/2')
        # Guest with bad session data
        session = {
            "guest_user": self.guest.serialize(),
                "redirect_action": {
                    "action": "edit_queue", 
                    "args": [self.queue1.id]
                    }
                }
        request = self.setup_session("/", session)
        request.user = AnonymousUser()
        response = views.index(request)
        print(response.status_code)
        self.assertEqual(response.status_code,302)
        path = response.headers["Location"]
        self.assertEqual(path, '/')

    def _test_index_logged_in(self):
        # Logged in
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("index"), follow=True)
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def test_profile_view(self):
        # Not Logged in
        response = self.client.get(reverse("profile"), follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)

    def _test_login_view(self):
        # Not Logged in
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign In", response.content)
        # Logged in
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("account_login"), follow=True)
        last_url, _ = response.redirect_chain[-1]
        self.assertEqual(last_url, "/profile")

    def _test_logout_view(self):
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("account_logout"))
        path = response.request.get("PATH_INFO")
        print(path)
        self.assertEqual(path, "/accounts/logout/")
        response = self.client.post(reverse("account_logout"), follow=True)
        path = response.request.get("PATH_INFO")
        print(response.dict())
        self.assertEqual(path, "/")

    def _test_return_from_authorization(self):
        sample = "?state=BJn&code=4Eg&scope=https://www.googleapis.com/auth/youtube"
        response = self.client.get(REDIRECT_URI + sample, follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(REDIRECT_URI + sample, follow=True)
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
