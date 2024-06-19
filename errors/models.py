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
        print(response)
        if status_code not in {200, 302}:
            msg = "An unknown error seems to have occurred."
            msg_type = messages.ERROR
            return False, msg, msg_type
        #request.session["last_path"] = request.path
        #return True, request,
        elif status_code == 302:
            return True, 'redirected', messages.INFO 
        return True, 'everything is a lie', messages.INFO