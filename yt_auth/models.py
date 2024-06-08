from django.db import models
import ast


# Create your models here.
class Credentials(models.Model):
    token = models.CharField(max_length=300, default="", null=True, blank=True)
    refresh_token = models.CharField(max_length=300, default="", null=True, blank=True)
    expiry = models.CharField(max_length=50, default="", null=True, blank=True)
    has_tokens = models.BooleanField(default=False)

    @classmethod
    def from_json(cls, json):
        creds = ast.literal_eval(json)
        creds['has_tokens']=True
        credentials = Credentials(creds)
        credentials.save()

    def to_dict(self):
        cred_dict = {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "expiry": self.expiry,
            "has_tokens": self.has_tokens,
        }
        return cred_dict

    def remove_credentials(self):
        self.token = ""
        self.refresh_token = ""
        self.expiry = ""
        self.has_tokens = False
        self.save()

    @property
    def has_tokens(self):
        return self.token != "" and self.refresh_token != ""
