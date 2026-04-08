from django.test import TestCase, RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from unittest.mock import patch
import json
from yt_auth.models import Credentials
from profiles.models import Profile, GuestProfile
from .models import Queue, Entry, has_authorization
from . import views


@override_settings(
    MIDDLEWARE_CLASSES=(
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    )
)
class QueueViewTestBase(TestCase):

    def mock_add_entry(self, queue, user, index: int):
        entry = Entry(**self.fake_video_result(index))
        entry.p_queue = queue
        entry.user = user.nickname
        entry._position = index
        entry.save()

    def fake_video_result(self, index: int) -> dict:
        video_result = {
            "kind": f"kind-{index}",
            "yt_id": f"id-{index}",
            "video_id": f"video-id-{index}",
            "title": f"title-{index}",
        }
        return video_result

    def make_get_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request

    def make_post_request(self, path, data):
        request = RequestFactory().post(path, data)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request

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
        for queue in [self.queue1, self.queue2]:
            queue.save()
            for _ in range(2):
                self.mock_add_entry(queue, queue.owner, _)

    def setUp(self):
        self.factory = RequestFactory()
        self.setup_users()
        self.setup_queues()
        self.guest = GuestProfile(name="Guest", email="Guest@McTestFace.com")


class _TestQueueMisc(QueueViewTestBase):

    # This stays here
    def test_has_authorization(self):
        self.assertTrue(has_authorization(self.user1, self.queue1.id))
        self.assertFalse(has_authorization(self.user1, self.queue2.id))
        self.guest.queue_id = self.queue1.id
        self.assertTrue(has_authorization(self.guest, self.queue1.id))
        self.assertFalse(has_authorization(self.guest, self.queue2.id))
    # Sync was tested manually

    # Assistant-written test
    def test_swap_same_position_returns_unchanged_entries(self):
        # Redundant coverage: mirrored in _TestSwapEndpoint at line 1192.
        queue = self.queue1
        entry = queue.all_entries[0]
        original_position = entry.position
        original_title = entry.title

        response = self.client.get(reverse("swap", args=[entry.id, entry.position]))
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["entry1"]["id"], entry.id)
        self.assertEqual(payload["entry2"]["id"], entry.id)
        self.assertEqual(payload["entry1"]["position"], original_position)
        self.assertEqual(payload["entry2"]["position"], original_position)
        self.assertEqual(payload["entry1"]["title"], original_title)
        self.assertEqual(payload["entry2"]["title"], original_title)

    # User-written test
    def test_gain_access_matching_data(self):
        # Redundant coverage: mirrored in _TestGainAccessEndpoint at lines 1203, 1213, and 1223.
        # Secrets don't match
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user2.secret]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("index"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Not logged in
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user1.secret]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("guest_sign_in"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest user
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(
            reverse("gain_access", args=[self.queue1.secret, self.user1.secret])
        )
        request.session = session
        request.user = AnonymousUser()
        response = views.gain_access(request, self.queue1.secret, self.user1.secret)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/queues/edit_queue/1")
        # Logged in, does not already have access
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("gain_access", args=[self.queue2.secret, self.user2.secret]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[self.queue2.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in, already has access
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user1.secret]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[self.queue1.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(["already in your list" in m.message for m in messages]))


# Checked that coverage matches old coverage
class _TestAddEntryEndpoint(QueueViewTestBase):

    # Assistant-written tests
    def test_add_entry_POST_rejects_anonymous(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "ok"
        old_queue_length = Queue.objects.get(id=self.queue1.id).length
        request = self.make_post_request(
            reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
            {"video_id": fake_video["video_id"]},
        )
        response = views.add_entry(request, self.queue1.id, fake_video["video_id"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("account_login"))
        self.assertEqual(Queue.objects.get(id=self.queue1.id).length, old_queue_length)

    # Assistant-written tests
    def test_add_entry_POST_rejects_unauthorized_guest(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "ok"
        old_queue_length = Queue.objects.get(id=self.queue1.id).length
        request = self.make_post_request(
            reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
            {"video_id": fake_video["video_id"]},
        )
        request.session = {"guest_user": self.guest.serialize()}

        response = views.add_entry(request, self.queue1.id, fake_video["video_id"])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("profile"))
        self.assertEqual(Queue.objects.get(id=self.queue1.id).length, old_queue_length)

    # Assistant-written tests
    def test_add_entry_POST_allows_authorized_guest(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "ok"

        self.guest.queue_id = self.queue1.id
        old_queue_length = self.queue1.length
        request = self.make_post_request(
            reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
            {"video_id": fake_video["video_id"]},
        )
        request.session = {"guest_user": self.guest.serialize()}
        with patch("queues.views.YT.find_video_by_id") as mock_find_video:
            mock_find_video.return_value = fake_video
            response = views.add_entry(request, self.queue1.id, fake_video["video_id"])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"], reverse("edit_queue", args=[self.queue1.id])
        )
        self.assertEqual(
            Queue.objects.get(id=self.queue1.id).length, old_queue_length + 1
        )

    # Assistant-written tests
    def test_add_entry_POST_rejects_unauthorized_user(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "ok"
        self.client.login(email="Testy2@McTestFace.com", password="myPassword")
        old_queue_length = self.queue1.length
        response = self.client.post(
            reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
            {"video_id": fake_video["video_id"]},
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(Queue.objects.get(id=self.queue1.id).length, old_queue_length)

    # Assistant-written tests
    def test_add_entry_POST_allows_owner(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "ok"
        old_queue_length = self.queue1.length
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")

        with patch("queues.views.YT.find_video_by_id") as mock_find_video:
            mock_find_video.return_value = fake_video
            response = self.client.post(
                reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
                {"video_id": fake_video["video_id"]},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Queue.objects.get(id=self.queue1.id).length, old_queue_length + 1
        )

    # Assistant-written tests
    def test_add_entry_POST_private_video_not_added(self):
        fake_video = self.fake_video_result(10)
        fake_video["status"] = "private"
        old_queue_length = Queue.objects.get(id=self.queue1.id).length
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")

        with patch("queues.views.YT.find_video_by_id") as mock_find_video:
            mock_find_video.return_value = fake_video
            response = self.client.post(
                reverse("add_entry", args=[self.queue1.id, fake_video["video_id"]]),
                {"video_id": fake_video["video_id"]},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Queue.objects.get(id=self.queue1.id).length, old_queue_length)


# Checked that coverage matches old coverage
class _TestCreateQueueEndpoint(QueueViewTestBase):
    
    # Assistant-written tests
    def test_GET_not_logged_in_redirects_login(self):
        response = self.client.get(reverse("create_queue"), follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    # Assistant-written tests
    def test_GET_guest_redirects_login(self):
        request = self.make_get_request(reverse("create_queue"))
        request.session = {"guest_user": self.guest.serialize()}
        response = views.create_queue(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], reverse("account_login"))

    # Assistant-written tests
    def test_GET_logged_in_renders_form(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("create_queue"))
        self.assertEqual(response.status_code, 200)
    
    # Assistant-written tests
    def test_POST_not_logged_in_redirects_login(self):
        data = {"queue-title": "New Test Queue Title", "queue-description": "desc"}
        response = self.client.post(reverse("create_queue"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], reverse("account_login"))

    # Assistant-written tests
    def test_POST_guest_redirects_to_login(self):
        data = {"queue-title": "New Test Queue Title", "queue-description": "desc"}
        request = self.make_post_request(reverse("create_queue"), data=data)
        request.session = {"guest_user": self.guest.serialize()}
        response = views.create_queue(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], reverse("account_login"))

    def test_POST_guest_does_not_create(self):
        count = Queue.objects.count()
        data = {"queue-title": "New Test Queue Title", "queue-description": "desc"}
        request = self.make_post_request(reverse("create_queue"), data=data)
        request.session = {"guest_user": self.guest.serialize()}
        views.create_queue(request)
        self.assertEqual(Queue.objects.count(), count)

    def test_POST_logged_in_redirects(self):
        data = {
            "queue-title": "New Test Queue Title",
            "queue-description": "New Test Queue Description",
        }
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.post(reverse("create_queue"), data, follow=True)
        new_queue = self.user1.my_queues.last()
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[new_queue.pk]),
            status_code=302,
            target_status_code=200,
        )

    # Assistant-written tests
    def test_POST_logged_in_creates(self):
        data = {
            "queue-title": "New Test Queue Title",
            "queue-description": "New Test Queue Description",
        }
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        old_user_count = self.user1.my_queues.count()
        self.client.post(reverse("create_queue"), data, follow=True)
        self.assertEqual(self.user1.my_queues.count(), old_user_count + 1)
        new_queue = self.user1.my_queues.last()
        self.assertEqual(new_queue.title, data["queue-title"])
        self.assertEqual(new_queue.description, data["queue-description"])

    # Assistant-written test
    def test_POST_create_queue_empty_title(self):
        queue_count = Queue.objects.count()
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")

        response = self.client.post(
            reverse("create_queue"),
            {"queue-title": "", "queue-description": "Should not create."},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Queue.objects.count(), queue_count)
        msgs = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn("Queue title cannot be empty.", msgs)


# Checked that coverage matches old coverage
class _TestEditQueueEndpoint(QueueViewTestBase):

    # Assistant-written tests
    def test_GET_not_logged_in_redirects_login(self):
        response = self.client.get(
            reverse("edit_queue", args=[self.queue1.id]), follow=True
        )
        self.assertRedirects(
            response, reverse("account_login"), status_code=302, target_status_code=200
        )

    # Assistant-written tests
    def test_GET_guest_without_auth_redirects_to_guest_login(self):
        request = self.make_get_request(reverse("edit_queue", args=[self.queue1.id]))
        request.session = {"guest_user": self.guest.serialize()}
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], reverse("guest_sign_in"))

    # Assistant-written tests
    def test_GET_guest_with_auth_renders(self):
        self.guest.queue_id = self.queue1.id
        request = self.make_get_request(reverse("edit_queue", args=[self.queue1.id]))
        request.session = {"guest_user": self.guest.serialize()}
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title) #str.encode(self.queue1.title)?

    # Assistant-written tests
    def test_GET_logged_in_without_auth_redirects_profile(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("edit_queue", args=[self.queue2.id]), follow=True
        )
        self.assertRedirects(
            response, reverse("profile"), status_code=302, target_status_code=200
        )

    # Assistant-written tests
    def test_GET_logged_in_with_auth_renders(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("edit_queue", args=[self.queue1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)
        # Todo: shouldn't I be checking the path of this?
        
    # Assistant-written tests
    def test_POST_not_logged_in_redirects_login(self):
        response = self.client.post(
            reverse("edit_queue", args=[self.queue1.id]),
            {"searchQuery": "sample"},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("account_login"), status_code=302, target_status_code=200
        )

    def test_POST_guest_without_auth_redirects_guest_login(self):
        request = self.make_post_request(
            reverse("edit_queue", args=[self.queue1.id]),
            {"searchQuery": "sample search query"},
        )
        request.session = {"guest_user": self.guest.serialize()}
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], reverse("guest_sign_in"))

    def test_POST_guest_with_auth_renders(self):
        self.guest.queue_id = self.queue1.id
        request = self.make_post_request(
            reverse("edit_queue", args=[self.queue1.id]),
            {"searchQuery": "sample search query"},
        )
        request.session = {"guest_user": self.guest.serialize()}
        with patch("queues.views.YT.search_videos") as mock_search_videos:
            mock_search_videos.return_value = []
            response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)
        self.assertContains(response, "sample search query")

    def test_POST_logged_in_without_auth_redirects_profile(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.post(
            reverse("edit_queue", args=[self.queue2.id]),
            {"searchQuery": "sample search query"},
            follow=True,
        )
        self.assertRedirects(
            response, reverse("profile"), status_code=302, target_status_code=200
        )

    def test_POST_logged_in_with_auth_renders(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        with patch("queues.views.YT.search_videos") as mock_search_videos:
            mock_search_videos.return_value = []
            response = self.client.post(
                reverse("edit_queue", args=[self.queue1.id]),
                {"searchQuery": "sample search query"},
                follow=True,
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)
        self.assertContains(response, "sample search query")

# Checked that coverage matches old coverage
class _TestPublishEndpoint(QueueViewTestBase):
    # Todo: is there anything else to test with this endpoint?
    def _set_channels(self):
        self.user1.youtube_channel = "test_channel1"
        self.user2.youtube_channel = "test_channel2"
        self.user1.save()
        self.user2.save()
    
    # Assistant-written tests
    def test_POST_has_auth_no_channel_redirects_edit(self):
        #request = self.make_get_request(reverse("publish", args=[self.queue1.id]))
        #response = views.publish(request, self.queue1.id)
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.post(reverse("publish", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["location"], reverse("edit_queue", args=[self.queue1.id])
        )

    # Assistant-written tests
    def test_POST_logged_in_not_owner_does_not_publish(self):
        self._set_channels()
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.post(reverse("publish", args=[self.queue2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Queue.objects.get(id=self.queue2.id).published)

    # Assistant-written tests
    def test_POST_owner_publishes_queue(self):
        self._set_channels()
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        with patch("queues.models.YT.create_playlist") as mock_create_playlist, patch(
            "queues.models.YT.add_entry_to_playlist"
        ) as mock_add_entry:
            mock_create_playlist.return_value = {
                "kind": "youtube#playlist",
                "id": "yt_playlist_test_id",
            }
            mock_add_entry.return_value = {
                "kind": "youtube#playlistItem",
                "id": "yt_entry_test_id",
            }
            response = self.client.post(reverse("publish", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        queue = Queue.objects.get(id=self.queue1.id)
        self.assertTrue(queue.published)
        self.assertTrue(queue.synced)

#Checked that coverage matches old coverage
class _TestDeleteQueueEndpoint(QueueViewTestBase):
    # Todo: these should not be get requests
    
    # Assistant-written tests
    def test_POST_not_logged_in_redirects_login(self):
        response = self.client.post(
            reverse("delete_queue", args=[self.queue1.id]), follow=True
        )
        self.assertRedirects(
            response, reverse("account_login"), status_code=302, target_status_code=200
        )

    # Assistant-written tests
    def test_POST_guest_without_auth_redirects_login(self):
        request = self.make_post_request(reverse("delete_queue", args=[self.queue1.id]), data={"sample":"sample"})
        request.session = {"guest_user": self.guest.serialize()}
        response = views.delete_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        # Todo: should this be redirecting to guest sign in?
        self.assertEqual(
            response.headers["Location"], reverse("account_login")
        )
    
    # TODO: Method should be changed to POST (delete_queue endpoint is POST-only).
    def test_POST_guest_with_auth_redirects_to_edit(self):
        self.guest.queue_id = self.queue1.id
        request = self.make_post_request(reverse("delete_queue", args=[self.queue1.id]), data={"sample":"sample"})
        request.session = {"guest_user": self.guest.serialize()}
        response = views.delete_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("edit_queue", args=[self.queue1.id]))
    
    # TODO: Method should be changed to POST (delete_queue endpoint is POST-only).
    def test_GET_logged_in_no_auth_redirects_profile(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_queue", args=[self.queue2.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
    # TODO: Method should be changed to POST (delete_queue endpoint is POST-only).
    def test_GET_logged_in_not_owner_with_auth_redirects_edit(self):
        self.user1.other_queues.add(self.queue2)
        self.user1.save()
        self.queue2.save()
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_queue", args=[self.queue2.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[self.queue2.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
    # Assistant-written tests
    # TODO: Method should be changed to POST (delete_queue endpoint is POST-only).
    def test_GET_owner_deletes_queue(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        old_num = len(self.user1.all_queues)
        response = self.client.get(
            reverse("delete_queue", args=[self.queue1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.get("PATH_INFO"), reverse("profile"))
        self.assertEqual(len(self.user1.all_queues), old_num - 1)

#Checked that coverage matches old coverage
class _TestDeleteEntryEndpoint(QueueViewTestBase):
    def setUp(self):
        super().setUp()
        self.entry = self.queue1.all_entries[0]
        self.original_length = self.queue1.length

    # Assistant-written tests
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_not_logged_in_redirects_login(self):
        response = self.client.get(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id]), follow=True
        )
        self.assertRedirects(
            response, reverse("account_login"), status_code=302, target_status_code=200
        )
    
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_guest_without_auth_redirects_profile(self):
        request = self.make_get_request(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id])
        )
        request.session = {"guest_user": self.guest.serialize()}
        response = views.delete_entry(request, self.queue1.pk, self.entry.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("edit_queue", args=[self.queue1.pk]))
        self.assertEqual(self.queue1.length, self.original_length)
        
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_guest_with_auth_redirects_profile(self):
        self.guest.queue_id = self.queue1.pk
        request = self.make_get_request(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id])
        )
        request.session = {"guest_user": self.guest.serialize()}
        response = views.delete_entry(request, self.queue1.pk, self.entry.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("edit_queue", args=[self.queue1.pk]))
        self.assertEqual(self.queue1.length, self.original_length)
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_logged_in_no_auth_redirects_profile(self):
        # Todo: doesn't user 1 have auth to queue 1?
        self.client.login(email="Testy2@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(self.queue1.length, self.original_length)
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_logged_in_not_owner_with_auth_redirects_edit(self):
        # Logged in user, not owner
        self.user2.other_queues.add(self.queue1)
        self.user2.save()
        self.client.login(email="Testy2@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[self.queue1.pk]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(self.queue1.length, self.original_length)

    # Assistant-written tests
    # TODO: Method should be changed to POST (delete_entry endpoint is POST-only).
    def test_GET_owner_deletes_entry(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[self.queue1.pk, self.entry.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.queue1.all_entries), self.original_length - 1)


class _TestSwapEndpoint(QueueViewTestBase):
    # Note, this is handled by Fetch and so there is no user validation on
    # the backend. However, the buttons to perform this action are only
    # displayed if the user is the queue owner.
    
    # Assistant-written tests
    def test_GET_swap_different_entries(self):
        entry1 = self.queue1.all_entries[0]
        entry1_old_position = entry1.position
        entry2 = self.queue1.all_entries[1]
        entry2_old_position = entry2.position
        response = self.client.get(reverse("swap", args=[entry1.id, entry2.position]))
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["entry1"]["position"], entry2_old_position)
        self.assertEqual(payload["entry2"]["position"], entry1_old_position)
        self.assertEqual(payload["entry1"]["id"], entry1.id)
        self.assertEqual(payload["entry2"]["id"], entry2.id)

    # Assistant-written tests
    def test_GET_swap_same_entry_position_unchanged(self):
        entry1 = self.queue1.all_entries[0]
        old = entry1.position
        title = entry1.title
        response = self.client.get(reverse("swap", args=[entry1.id, entry1.position]))
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["entry1"]["position"], old)
        self.assertEqual(payload["entry1"]["id"], entry1.id)
        self.assertEqual(payload["entry2"]["id"], entry1.id)
        self.assertEqual(payload["entry1"]["position"], old)
        self.assertEqual(payload["entry2"]["position"], old)
        self.assertEqual(payload["entry1"]["title"], title)
        self.assertEqual(payload["entry2"]["title"], title)


class _TestGainAccessEndpoint(QueueViewTestBase):
    # Assistant-written tests
    def test_GET_invalid_secret_redirects_index(self):
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user2.secret]),
            follow=True,
        )
        self.assertRedirects(
            response, reverse("index"), status_code=302, target_status_code=200
        )

    # Assistant-written tests
    def test_GET_not_logged_in_redirects_guest_sign_in(self):
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user1.secret]),
            follow=True,
        )
        self.assertRedirects(
            response, reverse("guest_sign_in"), status_code=302, target_status_code=200
        )

    # Assistant-written tests
    def test_GET_logged_in_existing_access_message(self):
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("gain_access", args=[self.queue1.secret, self.user1.secret]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[self.queue1.id]),
            status_code=302,
            target_status_code=200,
        )
        msg_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already in your list" in m.message for m in msg_list))
