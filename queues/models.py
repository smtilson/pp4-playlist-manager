from django.db import models
from profiles.models import Profile, make_user
from django.shortcuts import get_object_or_404
from yt_query.yt_api_utils import YT
from utils import get_secret
from mixins import DjangoFieldsMixin, ToDictMixin, ResourceID

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
    length = models.PositiveIntegerField(default=0)
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

    @classmethod
    def find_queue(cls, request, queue_id):
        return request, get_object_or_404(Queue, id=queue_id)

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
        # should this be refactored to require a key of some sort?
        if self.published:
            return f"Queue {self.title} is already uploaded to youtube."
        yt = YT(self.owner)
        # add some error checking here.
        response = yt.create_playlist(title=self.title, description=self.description)
        self.set_resource_id(response)
        for entry in self.all_entries:
            entry.publish(yt)
        for entry in self.deleted_entries:
            entry.delete()
        self.save()
        return f"Queue {self.title} successfully added to youtube."

    def test_publish(self):
        if self.published:
            msg = f"Queue {self.title} is already uploaded to youtube."
        else:
            msg = f"Queue {self.title} successfully added to youtube."
        self.yt_id="test_publish"
        for entry in self.all_entries:
            entry.test_publish()
        for entry in self.deleted_entries:
            entry.delete()
        self.save()
        return msg, [entry.to_dict() for entry in self.all_entries]

    @property
    def url(self):
        if self.published:
            return "https://www.youtube.com/playlist?list=" + self.yt_id
        return "#"

    # do not use this, it wastes resources
    def unpublish(self) -> None:
        if not self.published:
            print("This playlist isn't published yet.")
            return
        decision = input("Are you sure you want to do this? \n It wastes resources.")
        if decision != "yes":
            print("Thank you, exiting unpublish method.")
            return
        yt = YT(self.owner)
        response = yt.delete_playlist(self.yt_id)
        self.clear_resource_id()
        for entry in self.entries.all():
            entry.clear_resource_id()
        self.yt_id = ""
        self.save()
        print(response)

    def test_unpublish(self) -> None:
        if not self.published:
            print("This playlist isn't published yet.")
            return
        self.clear_resource_id()
        for entry in self.entries.all():
            entry.clear_resource_id()
        self.save()

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
        self.remove_excess(yt)
        self.resort()
        for entry in self.all_entries:
            if not entry.published:
                entry.publish(yt)
            elif not entry.synced:
                entry.sync(yt)
        self.save()
        
   
    def test_remove_excess(self):
        for entry in self.deleted_entries:
            entry.delete()

    def test_sync(self):
        self.remove_excess()
        self.resort()
        for entry in self.all_entries:
            if not entry.published:
                entry.test_publish()
            elif not entry.synced:
                entry.test_sync()
        self.save()
    
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
        print(f"Resort finished, {count} entries moved.")
        


class Entry(models.Model, DjangoFieldsMixin, ToDictMixin, ResourceID):
    title = models.CharField(max_length=100)
    p_queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="entries")
    video_id = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, default="")
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
    def test_publish(self):
        self.kind+='p'
        self.yt_id+= 'p'
        self.published = True
        self.synced = True
        self.save()
    
    def test_sync(self):
        self.kind+='s'
        self.yt_id+= 's'
        self.synced = True
        self.save()

    def to_dict(self) -> dict:
        return self.to_dict_mixin(self.field_names(), {"p_queue"})

    def sync(self, yt: "YT") -> None:
        response = yt.move_playlist_item(self)
        # add an error check here
        print(response)
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


def has_authorization(user, queue):
    if queue.id in getattr(user, "all_queue_ids", []):
        return True
    return False
