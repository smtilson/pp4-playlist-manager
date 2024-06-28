from django.db import models
from requests.exceptions import HTTPError
from profiles.models import Profile, make_user
from django.shortcuts import get_object_or_404
from yt_query.yt_api_utils import YT
from utils import get_secret
from mixins import DjangoFieldsMixin, ToDictMixin, ResourceID
from django.contrib import messages

# Create your models here.
MAX_QUEUE_LENGTH = YT.MAX_QUEUE_LENGTH


class Queue(models.Model, DjangoFieldsMixin, ToDictMixin, ResourceID):
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="my_queues", default=1
    )
    # what is the difference between this field and the yt_id below? Just that one interacts with the resource Id mixin?
    collaborators = models.ManyToManyField(Profile, related_name="other_queues")
    title = models.CharField(max_length=100, default="")
    description = models.TextField(max_length=400, null=True, blank=True, default="")
    # make these date names consistent throughout the app.
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    secret = models.CharField(max_length=20, unique=True, default=get_secret)
    kind = models.CharField(max_length=100, default="", null=True, blank=True)
    yt_id = models.CharField(max_length=100, default="", null=True, blank=True)

    def __str__(self):
        string = f"Queue: {self.title} by {self.owner}" + "\n"
        string += "\n".join([str(entry) for entry in self.all_entries])
        return string

    @property
    def full(self) -> bool:
        return self.length >= MAX_QUEUE_LENGTH

    @property
    def synced(self):
        if not self.published:
            return True
        for entry in self.entries.all():
            if not entry.synced:
                return False
        return True

    @property
    def length(self):
        return len(self.all_entries)

    def __len__(self):
        return self.length

    @property
    def all_entries(self):
        return [entry for entry in self.entries.all() if not entry.to_delete]

    @property
    def deleted_entries(self):
        return [entry for entry in self.entries.all() if entry.to_delete]

    def serialize(self):
        q_dict = self.to_dict_mixin(
            self.field_names(), {"entries", "owner", "date_created", "last_edited"}
        )
        q_dict["owner"] = self.owner.serialize()
        q_dict["date_created"] = str(self.date_created)
        q_dict["last_edited"] = str(self.last_edited)
        q_dict["entries"] = self.serialize_entries()
        return q_dict

    def serialize_entries(self):
        entries = self.entries.all()
        entries = [entry.to_dict() for entry in entries]
        return entries

    @property
    def published(self):
        return self.yt_id != ""

    def __getitem__(self, index: int):
        if index >= self.length:
            raise IndexError(
                f"Index must be valid, for example between 1 and {self.length}."
            )
        while index < 0:
            index += self.length
        return self.all_entries[index]

    def remove_entry(self, entry: "Entry") -> None:
        for other_entry in self.all_entries:
            if other_entry._position > entry._position:
                other_entry._position -= 1
                other_entry.save()
        entry.to_delete = True
        entry.synced = False
        entry.save()
        self.save()

    def publish(self) -> str:
        if self.published:
            return f"Queue {self.title} is already uploaded to youtube."
        yt = YT(self.owner)
        try:
            response = yt.create_playlist(title=self.title, description=self.description)
            self.set_resource_id(response)
            for entry in self.all_entries:
                entry.publish(yt)
        except HTTPError as e:
            msg += e
            msg_type = messages.ERROR
        else:
            for entry in self.deleted_entries:
                entry.delete()
            self.save()
            msg = f"Queue {self.title} successfully added to youtube."
            msg_type = messages.SUCCESS
        return msg, msg_type
        

    
    @property
    def url(self):
        if self.published:
            return "https://www.youtube.com/playlist?list=" + self.yt_id
        return "#"

    # do not use this, it wastes resources
    def unpublish(self) -> None:
        if not self.published:
            msg = "This playlist isn't published yet."
            msg_type = messages.INFO
            return msg, msg_type
        yt = YT(self.owner)
        try:
            yt.delete_playlist(self.yt_id)
        except HTTPError as e:
            msg = f"The following error occurred: {e}"
            msg_type = messages.ERROR
        else:
            msg = f"{self.title} has been removed from YouTube. To delete the"
            msg += "playlist from YouTube DJ, click the Delete button."
            msg_type = messages.SUCCESS
            self.clear_resource_id()
            for entry in self.entries.all():
                entry.clear_resource_id()
            self.yt_id = ""
            self.save()
        return msg, msg_type


    def pop(self, index: int = -1):
        entry = self[index]
        e_dict = entry.to_dict()
        entry.delete()
        self.length -= 1
        self.save()
        return e_dict

    def remove_excess(self, yt):
        for entry in self.deleted_entries:
            yt.remove_playlist_item(entry.yt_id)
            entry.delete()

    def sync(self):
        yt = YT(self.owner)
        try:
            self.remove_excess(yt)
            self.resort()
            for entry in self.all_entries:
                if not entry.published:
                    entry.publish(yt)
                elif not entry.synced:
                    entry.sync(yt)
            self.save()
        except HTTPError as e:
            msg = "An error occurred while trying to sync the Queue with YouTube."
            msg += str(e)
            msg_type = messages.ERROR
        else:
            msg = f"{self.title} has been synced with YouTube."
            msg_type = messages.SUCCESS
        return msg, msg_type
        
   
    

    
    def resort(self):
        positions = {entry._position for entry in self.all_entries}
        count = 0
        while len(positions) != self.length:
            for pos in positions:
                current = [
                    entry for entry in self.all_entries if entry._position == pos
                    ]
                if len(current) == 1:
                    continue
                for index, entry in enumerate(current):
                    entry._position = index + pos
                    count += 1
                    entry.save()


class Entry(models.Model, DjangoFieldsMixin, ToDictMixin, ResourceID):
    title = models.CharField(max_length=100)
    p_queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="entries")
    video_id = models.CharField(max_length=100)
    user = models.CharField(
        max_length=50, default="I am embarassed to have added this."
    )
    _position = models.IntegerField(default=-1)
    published = models.BooleanField(default=False)
    synced = models.BooleanField(default=False)
    # youtube_id = models.CharField(max_length=100,default="")
    kind = models.CharField(max_length=100, default="", null=True, blank=True)
    yt_id = models.CharField(max_length=100, default="", null=True, blank=True)
    to_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ["_position"]

    def __str__(self):
        return f"{self.position}. {self.title} added by {self.username}"
    
    @property
    def title_abv(self):
        if len(self.title) > 30:
            return self.title[:30]+"..."
        return self.title
    @property
    def username(self):
        if '@' in self.user:
            return self.user.split('@')[0]
        return self.user
    @property
    def playlist_id(self):
        return self.p_queue.yt_id

    @property
    def position(self):
        return self._position + 1

    @property
    def body(self):
        body = {
            "snippet": {
                "playlistId": self.playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": self.video_id},
            }
        }
        if self.published:
            body.update(self.resourceId)
            body["snippet"]["position"] = self._position
        return body

    def publish(self, yt: "YT") -> None:
        response = yt.add_entry_to_playlist(self.body)
        # add an error check here4
        self.set_resource_id(response)
        self.published = True
        self.synced = True
        self.save()
    
    def to_dict(self) -> dict:
        return self.to_dict_mixin(self.field_names(), {"p_queue"})

    def sync(self, yt: "YT") -> None:
        yt.move_playlist_item(self)
        self.synced = True
        self.save()

    @classmethod
    def swap_entries(cls, id_1, id_2):
        e1 = get_object_or_404(Entry, id=id_1)
        e2 = get_object_or_404(Entry, id=id_2)
        e1._position, e2._position = e2._position, e1._position
        e1.synced = False
        e2.synced = False
        e1.save()
        e2.save()

    def swap_entry_positions(self, other_position) -> None:
        if self.position == other_position:
            return
        other_entry = self.p_queue.all_entries[other_position - 1]
        self._position, other_entry._position = other_entry._position, self._position
        self.synced = False
        other_entry.synced = False        
        self.save()
        other_entry.save()
        return self, other_entry


def has_authorization(user, queue_id):
    if not user.is_authenticated and not user.is_guest:
        return False
    elif queue_id in getattr(user, "all_queue_ids", []):
        return True
    return False
