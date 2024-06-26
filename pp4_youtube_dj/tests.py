from profiles.models import Profile, GuestProfile
from django.urls import reverse
from django.test import TestCase
from queues.models import Queue


class TestBlogViews(TestCase):

    def setUp(self):
        self.user = Profile.objects.create_superuser(
            email="Testy@McTestFace.com",
            password="myPassword",
        )
        self.queue1 = Queue(
            owner=self.user,
            title="Test Queue1 Title",
            description="Test Queue1 Description",
            kind="",
            yt_id="",
        )
        self.queue2 = Queue(
            owner=self.user,
            title="Test Queue2 Title",
            description="Test Queue2 Description",
            kind="",
            yt_id="",
        )

        self.user.save()
        self.queue1.save()
        self.queue2.save()

    def _test_404_view(self):
        response = self.client.get("/404")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/asdfg")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/asdfg", follow=True)
        self.assertEqual(response.status_code, 404)
