from django.db import models
from django.contrib import messages

# Create your models here.

class RequestReport(models.Model):
    status_code = models.IntegerField()
    error_msg = models.CharField(max_length=500)
    session = models.JSONField()
    user_dict = models.JSONField()

    @classmethod
    def process(cls, response):
        status_code = response.status_code
        if status_code == 404:
            msg = "The page you requested does not exist."
            msg_type = messages.ERROR
        elif status_code not in {200, 302}:
            msg = "An unknown error seems to have occurred."
            msg_type = messages.ERROR
        #request.session["last_path"] = request.path
        #return True, request,
        elif status_code == 302:
            msg = 'You have been redirected.'
            msg_type = messages.INFO
        else:
            msg = 'Everything proceeded normally.'
            msg_type = messages.SUCCESS
        return status_code, msg, msg_type