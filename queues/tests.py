from django.test import TestCase, RequestFactory
from profiles.models import Profile, GuestProfile
from .models import Queue, Entry, has_authorization
from . import views
from yt_auth.models import Credentials
from django.shortcuts import reverse
import types
from django.contrib.messages import get_messages
from .views import (
    create_queue,
    publish,
    sync,
    gain_access,
    edit_queue,
    delete_queue,
    delete_entry,
)

# Create your tests here.


def test_publish_queue(queue):
    if queue.published:
        msg = f"Queue {queue.title} is already uploaded to youtube."
    else:
        msg = f"Queue {queue.title} successfully added to youtube."
    queue.yt_id = "test_publish"
    for entry in queue.all_entries:
        test_publish_entry(entry)
    for entry in queue.deleted_entries:
        entry.delete()
    queue.save()
    return msg, [entry.to_dict() for entry in queue.all_entries]


def test_unpublish(queue) -> None:
    if not queue.published:
        print("This playlist isn't published yet.")
        return
    queue.clear_resource_id()
    for entry in queue.entries.all():
        entry.clear_resource_id()
    queue.save()


def test_remove_excess(queue):
    for entry in queue.deleted_entries:
        entry.delete()


def test_sync_queue(queue):
    queue.remove_excess()
    queue.resort()
    for entry in queue.all_entries:
        if not entry.published:
            test_publish_entry(entry)
        elif not entry.synced:
            test_sync(entry)
    queue.save()


def test_publish_entry(entry):
    entry.kind += "p"
    entry.yt_id += "p"
    entry.published = True
    entry.synced = True
    entry.save()


def test_sync_entry(entry):
    entry.kind += "s"
    entry.yt_id += "s"
    entry.synced = True
    entry.save()


class TestQueueViews(TestCase):
    def mock_add_entry(self, queue, user, index: int):
        entry = Entry(**self.mock_video_result(index))
        entry.p_queue = queue
        entry.user = user.nickname
        entry._position = index
        entry.save()

    def mock_video_result(self, index: int) -> dict:
        video_result = {
            "kind": f"kind-{index}",
            "yt_id": f"id-{index}",
            "video_id": f"video-id-{index}",
            "title": f"title-{index}",
            "duration": f"duration-{index}",
        }
        return video_result

    def setup_session(self, path, session: dict = {}):
        request = self.factory.get(path)
        request.session = session
        return request

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
        for queue in [self.queue1, self.queue2]:
            queue.publish = types.MethodType(test_publish_queue, queue)
            queue.sync = types.MethodType(test_sync_queue, queue)
            queue.remove_excess = types.MethodType(test_remove_excess, queue)
            queue.unpublish = types.MethodType(test_unpublish, queue)
            queue.save()
            for _ in range(2):
                self.mock_add_entry(queue, queue.owner, _)
        self.guest = GuestProfile(name="Guest", email="Guest@McTestFace.com", queue_id=self.queue1.id)


    def _test_has_authorization(self):
        self.assertFalse(has_authorization(self.guest, self.queue2.id))
        self.assertTrue(has_authorization(self.user1, self.queue1.id))
        self.assertFalse(has_authorization(self.user1, self.queue2.id))
        self.assertTrue(has_authorization(self.guest, self.queue1.id))

    def test_create_queue(self):
        # Not logged in
        response = self.client.get(reverse("create_queue"), follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("create_queue"))
        self.assertEqual(response.status_code, 200)
        # Test Queue creation
        data = {
            "queue-title": "Test Queue Title",
            "queue-description": "Test Queue Description",
        }
        response = self.client.post(reverse("create_queue"), data, follow=True)
        self.assertEqual(self.user1.my_queues.all().count(), 2)
        new_queue = self.user1.my_queues.all().last()
        self.assertEqual(new_queue.title, "Test Queue Title")
        self.assertEqual(new_queue.description, "Test Queue Description")
        # Test Queue redirect after POST
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[new_queue.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def _test_edit_queue_user(self):
        # Not Logged in redirects to Login page
        response = self.client.get(
            reverse("edit_queue", args=[self.queue1.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in user without authorization
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("edit_queue", args=[self.queue2.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in user with authorization
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("edit_queue", args=[self.queue1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def _test_edit_queue_search(self):
        pass

    def test_edit_queue_guest(self):
        # Guest with authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.setup_session(reverse("edit_queue", args=[self.queue1.id]), session)
        request.user = self.guest
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 200)
        test_string = str.encode(self.queue1.title)
        self.assertContains(response, test_string)
        # Guest without authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.setup_session(reverse("edit_queue", args=[self.queue2.id]), session)
        request.user = self.guest
        response = views.edit_queue(request, self.queue2.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/accounts/login/")

    def test_publish(self):
        pass

    def _test_sync(self):
        # Not Owner
        response = self.client.get(reverse("sync", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("must be the owner", "-".join(messages))
        # Not Published
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("sync", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("must be published", "-".join(messages))
        # Already Synced
        self.queue1.publish()
        self.queue1.sync()
        response = self.client.get(reverse("sync", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("already synced", "-".join(messages))
        # Sync
        response = self.client.get(reverse("sync", args=[self.queue2.id]))

    def _test_gain_access(self):

        pass

    def test_delete_queue(self):
        # Not logged in
        response = self.client.get(reverse("delete_queue", args=[self.queue1.id]),follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Logged in user without authorization
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
        # Logged in user with authorization
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        old_num = len(self.user1.all_queues)
        response = self.client.get(
            reverse("delete_queue", args=[self.queue1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user1.all_queues), old_num-1)

    def test_delete_entry(self):
        pass
