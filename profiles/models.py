# code inspired by https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from pp4_youtube_dj.settings import DEBUG
from yt_auth.models import Credentials


# Create your models here.

UNIQUE = not DEBUG
SCOPES = ["https://www.googleapis.com/auth/youtube"]
UNIVERSE_DOMAIN = "googleapis.com"
TOKEN_URI = "https://oauth2.googleapis.com/token"


class ProfileManager(BaseUserManager):
    # there is an is_staff field that I am leaving out, mayeb this is required somewhere later
    def _create_profile(self, email, password, is_staff, is_superuser, **kwargs):
        # will this not be caught by form submission?
        if not email:
            raise ValueError("An email is necessary to create a profile.")
        # is this necessary
        now = timezone.now()
        # what does this do?
        email = self.normalize_email(email)
        profile = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True,
            last_login=now,
            date_joined=now,
            **kwargs,
        )
        profile.set_password(password)
        profile.save(using=self._db)
        return profile

    def create_profile(self, email, password, **kwargs):
        return self._create_profile(email, password, False, False, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        return self._create_profile(email, password, True, True, **kwargs)


DEFAULT_CREDENTIALS = Credentials()


class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=DEBUG)
    name = models.CharField(max_length=200, null=True, blank=True)
    is_superuser = models.BooleanField(default=DEBUG)
    is_staff = models.BooleanField(default=DEBUG)
    is_active = models.BooleanField(default=DEBUG)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    credentials = models.OneToOneField(
        Credentials,
        on_delete=models.SET_DEFAULT,
        null=True,
        default=Credentials
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = ProfileManager()

    def get_absolute_url(self):
        return f"/profiles/{self.pk}/"

    def remove_credentials(self):
        self.token = ""
        self.refresh_token = ""
        self.expiry = ""
        self.test_char_field = "credentials removed"
        self.save()
