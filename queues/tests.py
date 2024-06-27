from django.test import TestCase, RequestFactory, override_settings
from profiles.models import Profile, GuestProfile, make_user
from .models import Queue, Entry, has_authorization
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from . import views
from yt_auth.models import Credentials
from django.shortcuts import reverse
import types
import json
from django.contrib.messages import get_messages
from . import views

# Create your tests here.


def t_publish_queue(queue):
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


def t_unpublish(queue) -> None:
    if not queue.published:
        print("This playlist isn't published yet.")
        return
    queue.clear_resource_id()
    for entry in queue.entries.all():
        entry.clear_resource_id()
    queue.save()


def t_remove_excess(queue):
    for entry in queue.deleted_entries:
        entry.delete()


def t_sync_queue(queue):
    queue.remove_excess()
    queue.resort()
    for entry in queue.all_entries:
        if not entry.published:
            test_publish_entry(entry)
        elif not entry.synced:
            test_sync(entry)
    queue.save()


def t_publish_entry(entry):
    entry.kind += "p"
    entry.yt_id += "p"
    entry.published = True
    entry.synced = True
    entry.save()


def t_sync_entry(entry):
    entry.kind += "s"
    entry.yt_id += "s"
    entry.synced = True
    entry.save()


@override_settings(
    MIDDLEWARE_CLASSES=(
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    )
)
class TestQueueViews(TestCase):
    # the name of these methods should be changed since no real mocking is going on.
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
            "title": f"title-{index}"
        }
        return video_result
        #request = self.factory.get(path)
        #request.session = session
        #return request

    def make_get_request(self, path):
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
        request.session = {}
        return request
        request = RequestFactory().get(path)
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = AnonymousUser()
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
            queue.publish = types.MethodType(t_publish_queue, queue)
            queue.sync = types.MethodType(t_sync_queue, queue)
            queue.remove_excess = types.MethodType(t_remove_excess, queue)
            queue.unpublish = types.MethodType(t_unpublish, queue)
            queue.save()
            for _ in range(2):
                self.mock_add_entry(queue, queue.owner, _)

    def setUp(self):
        self.factory = RequestFactory()
        self.setup_users()
        self.setup_queues()
        self.guest = GuestProfile(name="Guest", email="Guest@McTestFace.com")

    def _test_has_authorization(self):
        self.assertTrue(has_authorization(self.user1, self.queue1.id))
        self.assertFalse(has_authorization(self.user1, self.queue2.id))
        self.guest.queue_id = self.queue1.id
        self.assertTrue(has_authorization(self.guest, self.queue1.id))
        self.assertFalse(has_authorization(self.guest, self.queue2.id))

    def _test_create_queue_GET(self):
        # Not logged in, GET request
        response = self.client.get(reverse("create_queue"), follow=True)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest, GET request
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("create_queue"))
        request.session = session
        response = views.create_queue(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["location"]
        self.assertEqual(path, reverse("account_login"))
        # Logged in, GET request
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("create_queue"))
        self.assertEqual(response.status_code, 200)
    
    def _test_create_queue_POST(self):
        queue_count = len(Queue.objects.all())
        data = {
            "queue-title": "New Test Queue Title",
            "queue-description": "New Test Queue Description",
        }
        # Not logged in
        request = self.make_post_request(reverse("create_queue"), data=data)
        response = views.create_queue(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["location"]
        self.assertEqual(path, reverse("account_login"))
        # Guest
        session = {"guest_user": self.guest.serialize()}
        request = self.make_post_request(reverse("create_queue"), data=data)
        request.session = session
        response = views.create_queue(request)
        self.assertEqual(response.status_code, 302)
        path = response.headers["location"]
        self.assertEqual(path, reverse("account_login"))
        self.assertEqual(len(Queue.objects.all()), queue_count)
        # Logged in, POST request
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        user_queue_count = self.user1.my_queues.all().count()
        response = self.client.post(reverse("create_queue"), data, follow=True)
        # Test queue creation
        self.assertEqual(self.user1.my_queues.all().count(), user_queue_count + 1)
        self.assertEqual(len(Queue.objects.all()), queue_count + 1)
        new_queue = self.user1.my_queues.all().last()
        self.assertEqual(new_queue.title, "New Test Queue Title")
        self.assertEqual(new_queue.description, "New Test Queue Description")
        # Redirect after POST
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[new_queue.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

    def _test_edit_queue_view_GET(self):
        # Not Logged in
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
        # Guest, no authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("edit_queue", args=[self.queue1.id]))
        request.session = session
        response = views.edit_queue(request, self.queue1.id)
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest, authorization
        self.guest.queue_id = self.queue1.id
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("edit_queue", args=[self.queue1.id]))
        request.session = session
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 200)
        # Logged in, no authorization
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

    def _test_edit_queue_guest(self):
        # Guest without authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("edit_queue", args=[self.queue2.id]))
        request.session = session
        request.user = self.guest
        response = views.edit_queue(request, self.queue2.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, "/accounts/login/")
        # Guest with authorization
        self.guest.queue_id = self.queue1.id
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("edit_queue", args=[self.queue1.id]))
        request.session = session
        response = views.edit_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 200)
        test_string = str.encode(self.queue1.title)
        self.assertContains(response, test_string)
        
    def _test_publish(self):
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

    def _test_delete_queue(self):
        # Not logged in
        response = self.client.get(
            reverse("delete_queue", args=[self.queue1.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest without authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("delete_queue", args=[self.queue1.id]))
        request.session = session
        response = views.delete_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        # First redirects to Edit Queue, which further redirects to Account Login
        self.assertEqual(path, reverse("edit_queue", args=[self.queue1.id]))
        # Guest with authorization
        self.guest.queue_id = self.queue1.id
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(reverse("delete_queue", args=[self.queue1.id]))
        request.session = session
        response = views.delete_queue(request, self.queue1.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[self.queue1.id]))
        # Logged in user without any authorization
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
        # Logged in user with authorization, not owner
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
        # Logged in, queue owner
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        old_num = len(self.user1.all_queues)
        response = self.client.get(
            reverse("delete_queue", args=[self.queue1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        path = response.request.get("PATH_INFO")
        self.assertEqual(path, reverse("profile"))
        self.assertEqual(len(self.user1.all_queues), old_num - 1)

    def _test_delete_entry(self):
        queue = self.queue1
        entry1 = queue.all_entries[0]
        original_length = queue.length
        # Not logged in
        response = self.client.get(
            reverse("delete_entry", args=[queue.id, entry1.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("account_login"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        # Guest without authorization
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(
            reverse("delete_entry", args=[queue.id, entry1.id])
        )
        request.session = session
        response = views.delete_entry(request, queue.id, entry1.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        # First redirects to Edit Queue, which further redirects to Account Login
        self.assertEqual(path, reverse("edit_queue", args=[queue.id]))
        self.assertEqual(queue.length, original_length)
        # Guest with authorization
        self.guest.queue_id = queue.id
        session = {"guest_user": self.guest.serialize()}
        request = self.make_get_request(
            reverse("delete_entry", args=[queue.id, entry1.id])
        )
        request.session = session
        response = views.delete_entry(request, queue.id, entry1.id)
        self.assertEqual(response.status_code, 302)
        path = response.headers["Location"]
        self.assertEqual(path, reverse("edit_queue", args=[queue.id]))
        self.assertEqual(queue.length, original_length)
        # Logged in user without any authorization
        self.client.login(email="Testy2@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[queue.id, entry1.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("profile"),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(queue.length, original_length)
        # Logged in user, not owner
        self.user2.other_queues.add(queue)
        self.user2.save()
        self.client.login(email="Testy2@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[queue.id, entry1.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("edit_queue", args=[queue.id]),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
        self.assertEqual(queue.length, original_length)
        # Logged in user, owner
        self.client.login(email="Testy1@McTestFace.com", password="myPassword")
        response = self.client.get(
            reverse("delete_entry", args=[queue.id, entry1.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(queue.all_entries), original_length - 1)

    def _test_swap(self):
        # Note, this is handled by Fetch and so there is no user validation on
        # the backend. However, the buttons to perform this action are only
        # displayed if the user is the queue owner.
        # Different entries
        queue = self.queue1
        entry1 = queue.all_entries[0]
        entry1_old_position = entry1.position
        entry2 = queue.all_entries[1]
        entry2_old_position = entry2.position
        response = self.client.get(reverse("swap", args=[entry1.id, entry2.position]))
        json_dict = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_dict["entry1"]["position"], entry2_old_position)
        self.assertEqual(json_dict["entry2"]["position"], entry1_old_position)
        # Same entry
        entry1_old_position = entry1.position
        response = self.client.get(reverse("swap", args=[entry1.id, entry1.position]))
        json_dict = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_dict["entry1"]["position"], entry1_old_position)
        self.assertEqual(json_dict["entry2"]["position"], entry2_old_position)

    def _test_gain_access_matching_data(self):
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
