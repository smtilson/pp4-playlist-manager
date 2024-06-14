profile_class_code_raw = (
    """email = models.EmailField(max_length=200, unique=DEBUG)
    name = models.CharField(max_length=200, null=True, blank=True)
    is_superuser = models.BooleanField(default=DEBUG)
    is_staff = models.BooleanField(default=DEBUG)
    is_active = models.BooleanField(default=DEBUG)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    credentials = models.OneToOneField(Credentials,on_delete=models.SET_DEFAULT,null=True,default=Credentials)
    youtube_id = models.CharField(max_length=100,null=True,blank=True, default='')
    youtube_url = models.CharField(max_length=100,null=True,blank=True, default='')"""
    """


"""
)

queue_class_fields = """owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="my_queues", default=1)
    owner_yt_id = models.CharField(max_length=100, default="")
    youtube_id = models.CharField(max_length=100, default="")
    collaborators = models.ManyToManyField(Profile, related_name="other_queues")
    name = models.CharField(max_length=100, default="none given")
    description = models.TextField(max_length=400, null=True, blank=True, default="")
    date_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    length = models.PositiveIntegerField(default=0)
    synced = models.BooleanField(default=False)
    secret = models.CharField(max_length=20,unique=True, default=get_secret)
"""

from profiles.models import Profile
from yt_auth.models import Credentials
from queues.models import Queue, Entry
from yt_query.yt_api_utils import YT, process_response
from utils import get_secret

me = Profile.objects.all().first()

all_queues = Queue.objects.all()
queue = all_queues[len(all_queues)-1]
base_url = "https://www.youtube.com/playlist?list="
playlist_url = "https://www.youtube.com/playlist?list=PLaPvip_wdwX0etylKbQJBY2PmpLkjIBHT"
playlist_id = "PLaPvip_wdwX0Z2KhcrSAZokbY8V_8eIRc"
yt = YT(me)

entry = queue[0]
entry2 = queue[2]
e_dict = entry.to_dict()
e_dict2 = entry2.to_dict()
sample_video_id1 = entry.video_id
sample_playlist_id = queue.yt_id

def add_entry_to_playlist(service, entry):
    request = service.user_service.playlistItems().insert(part="snippet,id", body=entry.body)
    response = request.execute()
    return process_response(response)

def move_playlist_item(service,entry:"Entry"):
    request = service.user_service.playlistItems().update(part="snippet,id", body=entry.body)
    response = request.execute()
    return process_response(response)

request = yt.guest_service.search().list(
            # maxResults=5 in order to limit API usage
            part="snippet",
            type="video",
            q="joe rogan freeway rick ross",
            maxResults=5,
        )





