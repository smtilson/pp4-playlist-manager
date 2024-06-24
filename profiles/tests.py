from .models import Profile, GuestProfile
from django.urls import reverse
from django.test import TestCase
from queues.models import Queue
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
        # Not Logged in
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        # Testing redirect to login
        response = self.client.get(reverse("profile"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In', html=True)
        # Logged in
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.queue1.title)
        
    def test_login_view(self):
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
        self.assertEqual(last_url,'/profile')

    def test_logout_view(self):
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(reverse("account_logout"))
        path = response.request.get("PATH_INFO")
        print(path)
        self.assertEqual(path,'/accounts/logout/')
        response = self.client.post(reverse("account_logout"), follow=True)
        path = response.request.get("PATH_INFO")
        self.assertEqual(path,'/')

    def test_return_from_authorization(self):
        sample = '?state=BJn&code=4Eg&scope=https://www.googleapis.com/auth/youtube'
        response = self.client.get(REDIRECT_URI+sample, follow=True)
        self.assertRedirects(response, reverse("account_login"), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.client.login(email="Testy@McTestFace.com", password="myPassword")
        response = self.client.get(REDIRECT_URI+sample, follow=True)
        self.assertRedirects(response, reverse("profile"), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

        