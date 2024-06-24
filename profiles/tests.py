import yt_auth.token_auth
from .models import Profile, GuestProfile, make_user
from . import views
import google.oauth2.credentials as g_oa2_creds
from yt_auth.models import Credentials
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch, MagicMock, Mock
from django.contrib.sessions.backends import db
from django.urls import reverse
from django.test import TestCase, RequestFactory
from queues.models import Queue
from django.http import HttpResponseRedirect
import os
from profiles.views import index
from django.test import RequestFactory
import yt_auth

if os.path.isfile("env.py"):
    import env

LOCAL = eval(os.environ.get("LOCAL"))
if LOCAL:
    REDIRECT_URI = "http://localhost:8000/"
else:
    REDIRECT_URI = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/"

sample = "?state=BJn&code=4Eg&scope=https://www.googleapis.com/auth/youtube"


class TestProfileViews(TestCase):
    # For these tests, I had to combine two different approaches. One uses
    # RequestFactory objects to make requests that can store data. This was
    # necessary, but less convenient than the other approach, will be evident.
    def setup_users(self):
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

    def old_setup_queues(self):
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

    def mock_queue(self, index: int) -> "Mock":
        mock_queue = Mock()
        mock_queue.owner = (self.user1,)
        mock_queue.id = index
        mock_queue.title = f"Test Queue Title {index}"
        mock_queue.description = (f"Test Queue Description{index}",)
        mock_queue.kind = ""
        mock_queue.yt_id = ""
        return mock_queue

    def setUp(self):
        self.factory = RequestFactory()
        self.setup_users()
        self.old_setup_queues()
        self.guest = GuestProfile(name="Guesty", email="Guesty@McTestFace.com")
        # self.guest.queue_id = self.queue1.id

    def google_creds(self):
        sample_token = {
            "universe_domain": "googleapis.com",
            "client_id": "secre.client.id.apps.googleusercontent.com",
            "token_uri": "https://oauth2.googleapis.com/token",
            "scopes": "['https://www.googleapis.com/auth/youtube']",
            "refresh_token": "1//refresh_token",
            "account": "",
            "client_secret": "client_secret",
            "has_tokens": True,
            "token": "token",
        }
        credentials = Credentials(**sample_token)
        return credentials.to_google_credentials()

    def make_get_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request

    def make_post_request(self, path, data: dict):
        request = RequestFactory().post(path, data)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request

    def _test_make_user(self):
        # Anonymous User
        request = self.make_get_request("/")
        user = make_user(request)
        self.assertFalse(user.is_authenticated)
        self.assertFalse(user.is_guest)
        # Guest User
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request("/")
        request.session = session
        user = make_user(request)
        self.assertFalse(user.is_authenticated)
        self.assertTrue(user.is_guest)
        # Logged in User
        request = self.make_get_request("/")
        request.user = self.user1
        user = make_user(request)
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_guest)

    def _test_index_no_code_no_redirect(self):
        # Anonymous User
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        # Guest with no redirect action
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request("/")
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 200)
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        path = response.request["PATH_INFO"]
        self.assertEqual(path, "/")

    def _test_index_redirect_action(self):
        # Guest with good session data
        self.guest.queue_id = self.queue2.id
        session = {
            "guest_user": self.guest.serialize(),
            "redirect_action": {"action": "edit_queue", "args": [self.queue2.id]},
        }
        request = self.make_get_request("/")
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/queues/edit_queue/2")
        # Guest with bad session data
        session = {
            "guest_user": self.guest.serialize(),
            "redirect_action": {"action": "edit_queue", "args": [self.queue1.id]},
        }
        request = self.make_get_request("/")
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 200)
        #path = response.headers["Location"]
        #self.assertEqual(path, "/")
        # Logged in with access
        session = {
            "redirect_action": {"action": "edit_queue", "args": [self.queue1.id]}
        }
        request = self.make_get_request("/")
        request.session = session
        request.user = self.user1
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/queues/edit_queue/1")
        # Logged in without access
        session = {
            "redirect_action": {"action": "edit_queue", "args": [self.queue2.id]}
        }
        request = self.make_get_request("/")
        request.session = session
        request.user = self.user1
        response = views.index(request)
        self.assertEqual(response.status_code, 200)

    def _test_index_has_code(self):
        # Note, these tests pass but an exception occurs.
        # Not logged in
        response = self.client.get(sample, follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(sample)
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(sample, follow=True)
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def _test_profile_view(self):
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
        # Guest
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("profile"))
        request.session = session
        response = views.profile(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)

    def _test_set_name(self):
        data = {"name": "test name"}
        old_nickname = self.user1.nickname
        # Not logged in GET request
        response = self.client.get(reverse("set_name"), follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(self.user1.nickname, old_nickname)
        # Not logged in POST request
        response = self.client.post(reverse("set_name"), data, follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertNotEqual(self.user1.nickname, "test name")
        # Validated User
        request = self.make_post_request(reverse("set_name"), data)
        request.user = self.user1
        response = views.set_name(request)
        path = response.headers["Location"]
        self.assertEqual(response.status_code, 302)
        self.assertEqual(path, reverse("profile"))
        self.assertEqual(self.user1.nickname, "test name")

    def _test_login_view(self):
        # Not Logged in
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        path = response.request["PATH_INFO"]
        self.assertEqual(path, "/accounts/login/")
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("account_login"), follow=True)
        self.assertRedirects(
            response,
            reverse("index"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def _test_logout_view(self):
        # Not logged in
        response = self.client.get(reverse("account_logout"), follow=True)
        self.assertRedirects(
            response,
            reverse("index"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("account_logout"))
        path = response.request.get("PATH_INFO")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(path, "/accounts/logout/")
        # Logout works
        response = self.client.post(reverse("account_logout"), follow=True)
        path = response.request.get("PATH_INFO")
        self.assertRedirects(
            response,
            reverse("index"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def _test_return_from_auth(self):
        # Not logged in
        request = self.make_get_request(REDIRECT_URI + sample)
        response = views.return_from_authorization(request)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        self.assertEqual(response.status_code, 302)
        # Logged in, approve access
        request = self.make_get_request(REDIRECT_URI + sample)
        request.user = self.user1
        with patch("profiles.views.get_tokens") as mock_get_tokens:
            mock_get_tokens.return_value = self.google_creds()
            with patch("profiles.models.Profile.find_youtube_data") as mock_yt_data:
                mock_yt_data.return_value = "test_channel", "test_handle"
                response = views.return_from_authorization(request)
                path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user1.has_tokens)
        # Logged in, deny access is handled by the index view and the function
        # error_in_path
    def test_revoke_auth(self):
        pass

    def test_guest_sign_in(self):
        pass