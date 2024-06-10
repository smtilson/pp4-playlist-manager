from django.db import models
from profiles.models import Profile, GuestProfile
from django.shortcuts import get_object_or_404

# Create your models here.


class Queue(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                             related_name="queues",default=1)
    collaborators = models.ManyToManyField(Profile)
    name = models.CharField(max_length=100, default="none given")
    description = models.TextField(max_length=400, null=True, blank=True, default='')
    #make these date names consistent throughout the app.
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    @classmethod
    def find_queue(cls, queue_id):
        return get_object_or_404(Queue, id=queue_id)

    def add_video(self,video):
        pass

    def remove_entry(self, number: int):
        pass

class Entry(models.Model):
    pass