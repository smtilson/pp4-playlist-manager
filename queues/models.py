from django.db import models
from profiles.models import Profile, GuestProfile
from django.shortcuts import get_object_or_404
from yt_query.yt_api_utils import YT
from utils import get_secret
from mixins import DjangoFieldsMixin,ToDictMixin, ResourceID

# Create your models here.

class Queue(models.Model, DjangoFieldsMixin, ToDictMixin, ResourceID):
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
    kind = models.CharField(max_length=100,default="",null=True,blank=True)
    yt_id = models.CharField(max_length=100, default="",null=True,blank=True)


    @classmethod
    def find_queue(cls, request, queue_id):
        queue = request.session.get("queue")
        if not queue:
            queue = get_object_or_404(Queue, id=queue_id)
            queue = queue.serialize()
            request.session["queue"] = queue
        elif queue['id'] != queue_id:
            queue = get_object_or_404(Queue,id=queue_id)
            queue = queue.serialize()
            request.session["queue"] = queue
        return request, queue
    
    def serialize(self):
        q_dict = self.to_dict_mixin(self.field_names(),{"entries",'owner',"date_created","last_edited"})
        q_dict['owner'] = self.owner.serialize()
        q_dict['date_created']=str(self.date_created)
        q_dict['last_edited']=str(self.last_edited)
        q_dict["entries"] = self.serialize_entries()
        return q_dict

    def serialize_entries(self):
        entries = self.entries.all()
        entries = [entry.to_dict() for entry in entries]
        return entries
    
    @property
    def published(self):
        return self.yt_id != ''

    def __getitem__(self,index:int):
        if index >= self.length:
            raise IndexError(f"Index must be valid, for example between 1 and {self.length}.")
        while index < 0:
            index += self.length
        return self.entries.all()[index]

    def remove_entry(self, entry: "Entry") -> None:
        for other_entry in self.entries.all():
            if other_entry.position> entry.position:
                other_entry.position -=1
                other_entry.save()
        self.length -=1
        entry.delete()
        self.save()

    def publish(self) -> str:
        # should this be refactored to require a key of some sort?
        if self.published:
            return f"Queue {self.name} already uploadeded to youtube."
        yt = YT(self.owner)
        # add some error checking here.
        response = yt.create_playlist(title=self.name, description=self.description)
        self.save_resource_id(response)
        for entry in self.entries.all():
            entry.publish(yt, self.yt_id)
        self.synced = True
        self.save()
        return f"Queue {self.name} successfully added to youtube."

    @property
    def url(self):
        if self.published:
            return "https://www.youtube.com/playlist?list="+self.yt_id
        return "#"

    # do not use this, it wastes resources
    def unpublish(self) -> None:
        decision = input("Are you sure you want to do this? \n It wastes resources.")
        if decision !="yes":
            print("Thank you, exiting unpublish method.")
            return
        if not self.published:
            return
        yt = YT(self.owner)
        response = yt.delete_playlist(self.yt_id)
        self.clear_resource_id()
        for entry in self.entries.all():
            entry.clear_resource_id()
        self.yt_id = ""
        self.synced = False
        self.save()
        print(response)
    
    def pop(self, index:int=-1):
        entry = self[index]
        e_dict = entry.to_dict()
        entry.delete()
        self.length -= 1
        self.save()
        return e_dict


    def sync(self):
        yt = YT(self.owner)
        for entry in self.entries.all():
            entry.sync(yt,self.yt_id)
        self.synced = True
        self.save()


class Entry(models.Model, DjangoFieldsMixin, ToDictMixin, ResourceID):
    title = models.CharField(max_length=100)
    p_queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="entries")
    video_id = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, default="")
    # this corresponds to the user who added the video to the queue
    # actually, make this a char field and base it on the name of the user.
    # then the on delete shit won't matter.
    user = models.CharField(max_length=50, default="I am embarassed to have added this.")
    position = models.IntegerField(default=-1)
    old_position = models.IntegerField(default=-1)
    published = models.BooleanField(default=False)
    synced = models.BooleanField(default=False)
    #youtube_id = models.CharField(max_length=100,default="")
    kind = models.CharField(max_length=100,default="",null=True,blank=True)
    yt_id = models.CharField(max_length=100, default="",null=True,blank=True)

    class Meta:
        ordering = ["position"]

    def publish(self, yt: "YT", youtube_playlist_id: str) -> None:
        response = yt.add_entry_to_playlist(self.video_id, youtube_playlist_id)
        # add an error check here
        self.save_resource_id(response)
        self.old_position = self.position
        self.published = True
        self.save()

    def to_dict(self) -> dict:
        return self.to_dict_mixin(self.field_names(),{"p_queue"})

    def sync(self, yt: "YT", youtube_playlist_id: str) -> None:
        if self.position != self.old_position:
            response = yt.move_playlist_item(self.video_id, youtube_playlist_id, self.position)
        # add an error check here
            self.old_position = self.position
            print(response)
        self.synced = True
        self.save()
    # refactor this to be a class method that only takes ids
    def swap(self,other) -> None:
        other = get_object_or_404(Entry,id=other['id'])
        self.position, other.position = other.position, self.position
        self.synced = False
        other.synced = False
        self.save()
        other.save()

    @classmethod
    def swap_entries(cls, id_1, id_2):
        e1 = get_object_or_404(Entry, id = id_1)
        e2 = get_object_or_404(Entry, id = id_2)
        e1.position, e2.position = e2.position, e1.position
        e1.synced = False
        e2.synced = False
        e1.save()
        e2.save()
        


    def earlier(self) -> None:
        if self.position != 1:
            other_entry =self.p_queue.entries.all().filter(position=self.position-1).first()
            self.swap(other_entry)

    def later(self) -> None:
        if self.position != self.p_queue.length:
            other_entry =self.p_queue.entries.all().filter(position=self.position+1).first()
            self.swap(other_entry)
        else:
            return
        
body_shape={
  "id": "YOUR_PLAYLIST_ITEM_ID",
  "snippet": {
    "playlistId": "YOUR_PLAYLIST_ID",
    "position": 1,
    "resourceId": {
      "kind": "youtube#video",
      "videoId": "YOUR_VIDEO_ID"
    }
  }
}
