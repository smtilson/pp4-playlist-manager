from django.db import models

# Create your models here.

class Profile(models.Model):
    """
    """
    username = models.CharField(max_length=100) #maybe should auto match with the youtube username
    email = models.EmailField()
    name = models.CharField(max_length=200)
    associated_youtube_account = models.Charfield() #user_id for youtube, how do I get this?
    token = models.CharField()
    refresh_token= models.CharField()
    expiry = models.DateTimeField()

