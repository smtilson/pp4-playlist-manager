from django.db import models
import ast


# Create your models here.
class Credentials(models.Model):
    # I think some of these fields could be removed since they do not actually
    # change, but perhaps it is easiest to leave them in for the time being
    token_uri = models.CharField(max_length=300, default="", null=True, blank=True)
    token = models.CharField(max_length=300, default="", null=True, blank=True)
    refresh_token = models.CharField(max_length=300, default="", null=True, blank=True)
    expiry = models.CharField(max_length=50, default="", null=True, blank=True)
    client_id = models.CharField(max_length=300, default="", null=True, blank=True)
    client_secret = models.CharField(max_length=300, default="", null=True, blank=True)
    scopes = models.CharField(max_length=200, default="", null=True, blank=True)
    universe_domain = models.CharField(
        max_length=300, default="", null=True, blank=True
    )
    account = models.CharField(max_length=300, default="", null=True, blank=True)
    has_tokens = models.BooleanField(default=False)

    @classmethod
    def from_json(cls, json):
        creds = ast.literal_eval(json)
        creds["has_tokens"] = True
        credentials = Credentials(**creds)
        credentials.save()
        return credentials

    def to_dict(self):
        cred_dict = {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "expiry": self.expiry,
            "has_tokens": self.has_tokens,
            "token_uri": self.token_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.scopes,
            "universe_domain": self.universe_domain,
            "account": self.account,
        }
        return cred_dict

    def reset(self):
        self.token = ""
        self.refresh_token = ""
        self.expiry = ""
        self.has_tokens = False
        self.save()
