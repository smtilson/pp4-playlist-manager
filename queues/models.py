from django.db import models
from profiles.models import Profile, GuestProfile
from django.shortcuts import get_object_or_404

# Create your models here.


class Queue(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE,
                             related_name="queues",default=1)
    owner_yt_id = models.CharField(max_length=100, default="")
    youtube_id = models.CharField(max_length=100, default="")
    collaborators = models.ManyToManyField(Profile)
    name = models.CharField(max_length=100, default="none given")
    description = models.TextField(max_length=400, null=True, blank=True, default='')
    #make these date names consistent throughout the app.
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    length = models.PositiveIntegerField(default=0)

    @classmethod
    def find_queue(cls, queue_id):
        return get_object_or_404(Queue, id=queue_id)

    def remove_entry(self, number: int):
        pass

class Entry(models.Model):
    title=models.CharField(max_length=100)
    queue=models.ForeignKey(Queue, on_delete=models.CASCADE)
    video_id=models.CharField(max_length=100)
    duration = models.CharField(max_length=100,default='')
    #this corresponds to the user who added the video to the queue
    # actually, make this a char field and base it on the name of the user.
    # then the on delete shit won't matter.
    user = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,default=1)
    number=models.IntegerField(default=-1)
    class Meta:
        ordering=["-number"]
        