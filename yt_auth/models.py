from django.db import models
from utils import json_to_dict
from mixins import DjangoFieldsMixin
import google.oauth2.credentials as g_oa2_creds


# Create your models here.
CREDENTIALS_FIELDS = {
    "token_uri",
    "token",
    "refresh_token",
    "client_id",
    "client_secret",
    "scopes",
    "universe_domain",
    "account",
    "has_tokens",
}


class Credentials(models.Model, DjangoFieldsMixin):
    token_uri = models.CharField(max_length=300, default="",
                                 null=True, blank=True)
    token = models.CharField(max_length=300, default="", null=True, blank=True)
    refresh_token = models.CharField(max_length=300, default="",
                                     null=True, blank=True)
    client_id = models.CharField(max_length=300, default="",
                                 null=True, blank=True)
    client_secret = models.CharField(max_length=300, default="",
                                     null=True, blank=True)
    scopes = models.CharField(max_length=200, default="",
                              null=True, blank=True)
    universe_domain = models.CharField(max_length=300, default="",
                                       null=True, blank=True)
    account = models.CharField(max_length=300, default="",
                               null=True, blank=True)
    has_tokens = models.BooleanField(default=False)

    def to_google_credentials(self):
        """
        Converts the current instance of the Credentials model to a Google
        Credentials object.
        Returns: g_oa2_creds.Credentials
        """
        creds_dict = self.to_dict()
        # This prevents a particular error from occurring.
        creds_dict["scopes"] = [creds_dict["scopes"][2:-2]]
        del creds_dict["has_tokens"]
        return g_oa2_creds.Credentials(**creds_dict)

    def to_dict(self):
        """
        Returns a dictionary representation of the Credentials object.
        Returns: dict
        """
        return {
            field_name: getattr(self, field_name)
            for field_name in CREDENTIALS_FIELDS
        }

    def set_credentials(self, new_credentials=None):
        """
        Sets the credentials for the current instance of the Credentials model.
        Args: new_credentials (g_oa2_creds.Credentials, optional)
        Returns: None
        """
        if new_credentials is None:
            has_tokens = False
            new_credentials = Credentials().to_dict()
        else:
            has_tokens = True
            new_credentials = json_to_dict(new_credentials.to_json())
        for field_name in CREDENTIALS_FIELDS:
            if field_name == "has_tokens":
                setattr(self, field_name, has_tokens)
            else:
                setattr(self, field_name, new_credentials[field_name])
        self.save()
