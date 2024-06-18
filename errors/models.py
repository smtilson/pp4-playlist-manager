from django.db import models
from django.contrib import messages

# Create your models here.

class RequestReport(models.Model):
    status_code = models.IntegerField()
    error_msg = models.CharField(max_length=500)
    session = models.JSONField()
    user_dict = models.JSONField()

    @classmethod
    def process(cls, request):
        status_code = 200 #request.status_code
        
        if status_code != 200:
            msg = "An unknown error seems to have occurred."
            msg_type = messages.ERROR

            return False, msg, msg_type
        #request.session["last_path"] = request.path
        #return True, request, 
        return True, 'everything is a lie', messages.INFO