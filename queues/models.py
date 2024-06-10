from django.db import models
from profiles.models import Profile, GuestProfile

# Create your models here.

class Queue(models.Model):
    #owner = models.ForeignKey()
    #collaborators = models.ForeignKey()
    pass

    @classmethod
    def find_queue(cls, queue_id):
        pass

    def add_video(self,video):
        pass

    def remove_entry(self, number: int):
        pass

class Entry(models.Model):
    pass