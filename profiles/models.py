# I used code from the following article:
# https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318
# Below, when I refer to a link or article, the above is what is meant.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from utils import get_secret, format_field_name
from yt_auth.models import Credentials
from yt_query.yt_api_utils import YT
from mixins import ToDictMixin, DjangoFieldsMixin
from typing import Union


# Create your models here.
# I don't think these are used.
SCOPES = ["https://www.googleapis.com/auth/youtube"]
UNIVERSE_DOMAIN = "googleapis.com"
TOKEN_URI = "https://oauth2.googleapis.com/token"


class ProfileManager(BaseUserManager):
    # This class and the accompanying methods were taken from the above link.
    def _create_profile(self, email, password, is_staff, is_superuser, **kwargs):
        if not email:
            raise ValueError("An email is necessary to create a profile.")
        now = timezone.now()
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


class Profile(AbstractBaseUser, PermissionsMixin, DjangoFieldsMixin, ToDictMixin):
    # The basis of this class was taken from the article.
    # The methods and many of the fields are original work and not taken from the article..
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    credentials = models.OneToOneField(
        Credentials,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
    )
    youtube_channel = models.CharField(max_length=100, null=True, blank=True, default="")
    youtube_handle = models.CharField(max_length=100, null=True, blank=True, default="")
    secret = models.CharField(max_length=20, unique=True, default=get_secret)

    # These three variables are taken from the article.
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    # This variable is taken from the article.
    objects = ProfileManager()

    @property
    def is_guest(self):
        return False

    @property
    def nickname(self):
        if self.name:
            return self.name
        return self.email.split('@')[0]

    def to_dict(self):
        credentials = self.credentials.to_dict()
        p_dict = self.to_dict_mixin(
            self.field_names(), {"last_login", "date_joined", "credentials"}
        )
        p_dict["last_login"] = str(self.last_login)
        p_dict["date_joined"] = str(self.date_joined)
        p_dict["credentials"] = credentials
        p_dict["is_guest"] = False
        return p_dict

    @property
    def info_dict(self):
        return {"Name": self.nickname, "Email": self.email}

    # I should only have one of these maybe?
    def serialize(self):
        return self.to_dict()

    @property
    def has_tokens(self):
        return getattr(self.credentials, "has_token", False)

    def all_queues(self):
        pass

    def initialize(self):
        self.credentials = Credentials()
        self.credentials.save()
        self.save()

    @property
    def all_queue_ids(self):
        my_queue_ids = {queue.id for queue in self.my_queues.all()}
        other_queue_ids = {queue.id for queue in self.other_queues.all()}
        return my_queue_ids.union(other_queue_ids)
    @property
    # is this used?
    # this needs to be properly addressed
    def valid_credentials(self):
        if self.credentials.expiry == "":
            return False
        return self.google_credentials.valid

    def set_credentials(self, new_credentials=None):
        """
        new_credentials is a google Credentials object. Updates credentials to
        with the data from new_credentials. When no object is passed, it resets
        the credentials to the default blank credentials.
        """
        # attention: why am I not saving here.
        self.credentials.set_credentials(new_credentials)
        if self.has_tokens and not (self.youtube_handle or self.youtube_channel):
            self.find_youtube_data()
            msg = f"Successfully connected the youtube account {self.youtube_handle} to your profile."
        else:
            msg = f"Successfully updated credentials for {self.nickname}."
        return msg

    def find_youtube_data(self):
        yt = YT(self)
        self.youtube_channel, self.youtube_handle = yt.find_user_youtube_data()
        self.save()

    def revoke_youtube_data(self):
        """
        Removes youtube identification and credentials from system.
        """
        self.youtube_channel = ""
        self.youtube_handle = ""
        self.set_credentials()
        # i think this is unnecessary
        self.save()

    @property
    def google_credentials(self):
        return self.credentials.to_google_credentials()


class GuestProfile(ToDictMixin):
    def __init__(
        self,
        name: str = "",
        queue_id: int = 0,
        queue_secret: str = "",
        owner_secret: str = "",
        email: str = "",
    ) -> None:
        self.name = name
        self.queue_id = queue_id
        self.queue_secret = queue_secret
        self.owner_secret = owner_secret
        self.email = email
        self.is_superuser = False
        self.is_staff = False
        self.is_active = True
        self.is_guest = True
        self.is_authenticated = False
        # maybe replace these two with some datetime stuff
        self.last_login = ""
        self.date_joined = "not applicable"
        self.credentials = ""
        self.youtube_channel = ""
        self.youtube_handle = ""
        self.secret = ""
        self.has_tokens = False
        self.valid_credentials = False

    @property
    def nickname(self):
        return self.name

    def serialize(self):
        return self.to_dict_mixin(
            {"name", "queue_id", "queue_secret", "email", "owner_secret"}
        )

    @property
    def all_queue_ids(self):
        return [self.queue_id]
    
    def convert_to_profile(self):
        pass
    @property
    def info_dict(self):
        return {"Name": self.nickname, "Email": self.email}



def make_user(request) -> Union["Profile", "GuestProfile"]:
    # anonymous or authenticated
    user = request.user
    # a dict or none
    guest = request.session.get("guest_user")
    if guest:
        user = GuestProfile(**guest)
    elif not user.is_authenticated:
        user = GuestProfile()
        user.is_guest = False
    return user
