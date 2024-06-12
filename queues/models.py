from django.db import models
from profiles.models import Profile, GuestProfile
from django.shortcuts import get_object_or_404
from yt_query.yt_api_utils import YT
from utils import get_secret, DjangoFieldsMixin,ToDictMixin

# Create your models here.


class Queue(models.Model, DjangoFieldsMixin, ToDictMixin):
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="my_queues", default=1
    )
    owner_yt_id = models.CharField(max_length=100, default="")
    youtube_id = models.CharField(max_length=100, default="")
    collaborators = models.ManyToManyField(Profile, related_name="other_queues")
    name = models.CharField(max_length=100, default="none given")
    description = models.TextField(max_length=400, null=True, blank=True, default="")
    # make these date names consistent throughout the app.
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    length = models.PositiveIntegerField(default=0)
    synced = models.BooleanField(default=False)
    secret = models.CharField(max_length=20,unique=True, default=get_secret)

    @classmethod
    def find_queue(cls, queue_id):
        return get_object_or_404(Queue, id=queue_id)
    
    def serialize(self):
        q_dict = self.to_dict_mixin(self.field_names(),{'owner',"date_created","last_edited"})
        q_dict['owner'] = self.owner.id
        q_dict['date_created']=str(self.date_created)
        q_dict['last_edited']=str(self.last_edited)
        return q_dict

    @property
    def published(self):
        return self.youtube_id != ''

    def remove_entry(self, number: int):
        pass

    def publish(self) -> str:
        if self.published:
            return f"Queue {self.name} already uploadeded to youtube."
        yt = YT(self.owner)
        # add some error checking here.
        youtube_id = yt.create_playlist(title=self.name, description=self.description)
        self.youtube_id = youtube_id
        for entry in self.entries.all():
            entry.publish(yt, youtube_id)
        self.synced = True
        self.save()
        return f"Queue {self.name} successfully added to youtube."

    def sync(self):
        self.synced = True
        self.save()
        pass


class Entry(models.Model):
    title = models.CharField(max_length=100)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="entries")
    video_id = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, default="")
    # this corresponds to the user who added the video to the queue
    # actually, make this a char field and base it on the name of the user.
    # then the on delete shit won't matter.
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, default=1)
    number = models.IntegerField(default=-1)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["number"]

    def publish(self, yt: "YT", youtube_playlist_id: str) -> None:
        response = yt.add_entry_to_playlist(self.video_id, youtube_playlist_id)
        # add an error check here
        self.published = True
        self.save()
