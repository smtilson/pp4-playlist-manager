# code inspired by https://medium.com/@ksarthak4ever/django-custom-user-model-allauth-for-oauth-20c84888c318
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from pp4_youtube_dj.settings import DEBUG
import ast

# Create your models here.

UNIQUE = not DEBUG
SCOPES= ["https://www.googleapis.com/auth/youtube"]
UNIVERSE_DOMAIN = "googleapis.com"    
TOKEN_URI="https://oauth2.googleapis.com/token"
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
        profile = self.model(email=email,is_staff=is_staff, is_superuser=is_superuser, is_active=True,
                             last_login=now, date_joined=now, **kwargs)
        profile.set_password(password)
        profile.save(using=self._db)
        return profile
    
    def create_profile(self, email, password, **kwargs):
        return self._create_profile(email, password, False, False, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        return self._create_profile(email, password, True, True, **kwargs)
    
class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=DEBUG)
    name = models.CharField(max_length=200, null=True, blank=True)
    is_superuser = models.BooleanField(default=DEBUG)
    is_staff = models.BooleanField(default=DEBUG)
    is_active = models.BooleanField(default=DEBUG)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=300, default='', null=True, blank=True)
    refresh_token = models.CharField(max_length=300, default='', null=True, blank=True)
    # not sure how to handle a default empty DateTimeField
    expiry = models.CharField(max_length=50, default='',null=True, blank=True)
    test_char_field = models.CharField(max_length=300, default='', null=True, blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = ProfileManager()

    def get_absolute_url(self):
        return f"/profiles/{self.pk}/"
    

    def add_credentials(self, credentials):
        print(credentials)
        if isinstance(credentials, str):
            credentials = ast.literal_eval(credentials)
        elif not isinstance(credentials, dict):
            raise TypeError(f"credentials argument is type {type(credentials)}.")
        print(credentials)
        self.token = credentials['token']
        print(self.token)
        self.refresh_token = credentials['refresh_token']
        print(self.refresh_token)
        self.expiry = credentials['expiry']
        print(self.expiry)
        self.save()
        print(self.get_credentials())

    def get_credentials(self) -> dict[str:str]:
        print("calling get credentials")
        credentials = {'token': self.token,
                       'refresh_token': self.refresh_token,
                       'expiry': self.expiry}
        print(credentials)
        return credentials



'''class Profile(models.Model):


    username = models.CharField(max_length=100) #maybe should auto match with the youtube username
    email = models.EmailField()
    name = models.CharField(max_length=200)
    associated_youtube_account = models.CharField() #user_id for youtube, how do I get this?
    token = models.CharField()
    refresh_token= models.CharField()
    expiry = models.DateTimeField()
'''
