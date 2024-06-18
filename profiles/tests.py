from .models import Profile, GuestProfile
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

    def test_profile_view(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        
    '''def test_render_post_detail_page_with_comment_form(self):
        response = self.client.get(reverse("post_detail", args=["blog-title"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Blog title", response.content)
        self.assertIn(b"Blog content", response.content)
        self.assertIsInstance(response.context["comment_form"], CommentForm)'''
