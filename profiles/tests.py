from .models import Profile, GuestProfile, make_user
from . import views
import google.oauth2.credentials as g_oa2_creds
from yt_auth.models import Credentials
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch, MagicMock, Mock
from django.contrib.sessions.backends import db
from django.urls import reverse
from django.test import TestCase, RequestFactory, override_settings
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

sample_code = "?state=BJn&code=4Eg&scope=https://www.googleapis.com/auth/youtube"
sample_error = "?error=access_denied&state=random_state_string"

@override_settings(
    MIDDLEWARE_CLASSES=(
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    )
)
class TestProfileViews(TestCase):
    # For these tests, I had to combine two different approaches. One uses
    # RequestFactory objects to make requests that can store data. This was
    # necessary, but less convenient than the other approach, will be evident.
    # Note: the login, logout, and signup views are all halndled by all-auth
    # and I therefore did not test them.
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

    def setup_queues(self):
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

    def setUp(self):
        self.setup_users()
        self.setup_queues()
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

    def _test_index(self):
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
        # Guest with queue_id
        self.guest.queue_id = self.queue1.id
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request("/")
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, f"/queues/edit_queue/{self.queue1.id}")
        # Code present
        response = self.client.get(sample_code)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("return_from_authorization"))
        # Redirect action in session
        session = {"redirect_action": "edit_queue", "queue_id": self.queue1.id}
        request = self.make_get_request("/")
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("redirect_action"))

    def _test_redirect_action(self):
        # Guest with good redirect action
        self.guest.queue_id = self.queue2.id
        session = {
            "guest_user": self.guest.serialize(),
            "redirect_action": "edit_queue",
            "queue_id": self.queue2.id,
        }
        request = self.make_get_request("redirect_action")
        request.session = session
        response = views.redirect_action(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[self.queue2.id]))
        # Guest with invalid redirect data
        session = {
            "guest_user": self.guest.serialize(),
            "redirect_action": "edit_queue",
            "queue_id": self.queue1.id,
        }
        request = self.make_get_request(reverse("redirect_action"))
        request.session = session
        response = views.redirect_action(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/")
        # Logged in with access
        session = {"redirect_action": "edit_queue", "queue_id": self.queue1.id}
        request = self.make_get_request(reverse("redirect_action"))
        request.session = session
        request.user = self.user1
        response = views.redirect_action(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/queues/edit_queue/1")
        # Logged in without access
        session = {"redirect_action": "edit_queue", "queue_id": self.queue2.id}
        request = self.make_get_request(reverse("redirect_action"))
        request.session = session
        request.user = self.user1
        response = views.redirect_action(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/")

    def _test_index_error_code(self):
        url = REDIRECT_URI + sample_error
        # Not logged In
        request = self.make_get_request(url)
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        # Guest
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(url)
        request.session = session
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        # Logged in
        request = self.make_get_request(url)
        request.user = self.user1
        response = views.index(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))

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

    def _test_return_from_auth(self):
        # Not logged in
        request = self.make_get_request(REDIRECT_URI + sample_code)
        response = views.return_from_authorization(request)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        self.assertEqual(response.status_code, 302)
        # Guest
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(sample_code)
        request.session = session
        response = views.return_from_authorization(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        # Logged in, approve access
        request = self.make_get_request(REDIRECT_URI + sample_code)
        request.user = self.user1
        with patch("profiles.views.get_tokens") as mock_get_tokens:
            mock_get_tokens.return_value = self.google_creds()
            with patch("profiles.models.YT.find_user_youtube_data") as mock_yt_data:
                mock_yt_data.return_value = "test_channel", "test_handle"
                response = views.return_from_authorization(request)
                path = response.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        self.assertEqual(response.status_code, 302)
        # Check Tokens
        self.assertTrue(self.user1.has_tokens)
        # Check YouTube Data
        self.assertEqual(self.user1.youtube_channel, "test_channel")
        self.assertEqual(self.user1.youtube_handle, "test_handle")
        # Logged in, deny access is handled by the index view

    def _test_revoke_auth(self):
        # Not logged in
        response = self.client.get(reverse("revoke_authorization"), follow=True)
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
        request = self.make_get_request(reverse("revoke_authorization"))
        request.session = session
        response = views.revoke_authorization(request)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("account_login"))
        self.assertEqual(response.status_code, 302)
        # Logged in
        # Acquire tokens
        request1 = self.make_get_request(REDIRECT_URI + sample_code)
        request1.user = self.user1
        with patch("profiles.views.get_tokens") as mock_get_tokens:
            mock_get_tokens.return_value = self.google_creds()
            with patch("profiles.models.YT.find_user_youtube_data") as mock_yt_data:
                mock_yt_data.return_value = "test_channel", "test_handle"
                response1 = views.return_from_authorization(request1)
        data = {
            self.user1.has_tokens,
            self.user1.youtube_handle,
            self.user1.youtube_channel,
        }
        if not all(data):
            raise ValueError("Tokens and data were not mocked/acquired.")
        request2 = self.make_get_request(reverse("revoke_authorization"))
        request2.user = self.user1
        response2 = views.revoke_authorization(request2)
        path = response2.headers["Location"]
        self.assertEqual(path, reverse("profile"))
        self.assertEqual(response.status_code, 302)
        data = {
            self.user1.has_tokens,
            self.user1.youtube_handle,
            self.user1.youtube_channel,
        }
        self.assertFalse(any(data))

    def _test_guest_sign_in_GET(self):
        # No queue in session
        response = self.client.get(reverse("guest_sign_in"), follow=True)
        self.assertEqual(response.status_code, 404)
        # self.assertEqual(path, "404")
        # Queue in session, not logged in, GET request
        session = {"queue_id": self.queue1.id}
        request = self.make_get_request(reverse("guest_sign_in"))
        request.user = AnonymousUser()
        request.session = session
        response = views.guest_sign_in(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str.encode(self.queue1.title))
        # Queue in session, logged in
        session = {"queue_id": self.queue1.id}
        request = self.make_get_request(reverse("guest_sign_in"))
        request.user = self.user1
        request.session = session
        response = views.guest_sign_in(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[self.queue1.id]))
        # Queue in session, guest
        session = {"queue_id": self.queue1.id, "guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("guest_sign_in"))
        request.session = session
        response = views.guest_sign_in(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[self.queue1.id]))

    def _test_guest_sign_in_POST(self):
        # No queue in session
        response = self.client.post(reverse("guest_sign_in"), follow=True)
        self.assertEqual(response.status_code, 404)
        # Queue in session
        session = {"queue_id": self.queue1.id}
        data = {"guest_name": "guest_test_name", "guest_email": "guest_test_email"}
        request = self.make_post_request(reverse("guest_sign_in"), data)
        request.session = session
        response = views.guest_sign_in(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[self.queue1.id]))
        user = make_user(request)
        self.assertTrue(user.is_guest)
        self.assertEqual(user.name, data["guest_name"])
        self.assertEqual(user.email, data["guest_email"])
        self.assertTrue(has_authorization(user, self.queue1.id))
