from django.test import TestCase
from profiles.models import Profile
from .models import Queue, Entry
from django.shortcuts import reverse
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


class TestQueueViews(TestCase):
    def mock_add_entry1(self, index:int):
        entry = Entry(**self.mock_video_result(index))
        entry.p_queue = self.queue1
        entry.user = self.user.nickname
        entry._position = index
        entry.save()

    def mock_add_entry2(self, index:int):
        entry = Entry(**self.mock_video_result(index))
        entry.p_queue = self.queue2
        entry.user = self.user.nickname
        entry._position = index
        entry.save()
        
    def mock_video_result(self,index:int) -> dict:
        video_result = {
            "kind": f"kind-{index}",
            "yt_id": f"id-{index}",
            "video_id": f"video-id-{index}",
            "title": f"title-{index}",
            "duration": f"duration-{index}",
        }
        return video_result

    def setUp(self):
        self.user = Profile.objects.create_superuser(
            email="Testy@McTestFace.com",
            password="myPassword",
        )
        self.user.save()
        self.queue1 = Queue(
            owner=self.user,
            title="Test Queue1 Title",
            description="Test Queue1 Description",
            kind="",
            yt_id="",
        )
        self.queue1.save()
        self.queue2 = Queue(
            owner=self.user,
            title="Test Queue2 Title",
            description="Test Queue2 Description",
            kind="",
            yt_id="",
        )
        self.queue2.save()
        for _ in range(4):
            self.mock_add_entry1(_)
            self.mock_add_entry2(_)
        
    
    def test_create_queue(self):
        response = self.client.get(reverse("create_queue"))
        self.assertEqual(response.status_code, 302)
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("create_queue"))
        self.assertEqual(response.status_code, 200)
        data = {"queue-title":"Test Queue Title", "queue-description":"Test Queue Description"}
        response = self.client.post(reverse("create_queue"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.my_queues.all().count(), 3)
        new_queue = slef.user.my_queues.all().last()
        self.assertEqual(new_queue.title, "Test Queue Title")
        self.assertEqual(new_queue.description, "Test Queue Description")

    def test_edit_queue(self):
        response = self.client.get(reverse("edit_queue", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 302)
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("edit_queue", args=[self.queue1.id]))
        self.assertEqual(response.status_code, 200)
        
        self.client.post(reverse("create_queue"), data)
        self.assertEqual(self.user.my_queues.all().count(), 3)
        new_queue = slef.user.my_queues.all().last()
        self.assertEqual(new_queue.title, "Test Queue Title")
        self.assertEqual(new_queue.description, "Test Queue Description")

        pass

    def test_publish(self):

        pass

    def test_sync(self):

        pass

    def test_gain_access(self):

        pass

    def test_delete_queue(self):
        pass

    def test_delete_entry(self):
        pass
