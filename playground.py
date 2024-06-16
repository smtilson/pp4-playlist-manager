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
from yt_auth.token_auth import revoke_tokens
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

#sample_video_id1 = entry.video_id
#sample_playlist_id = queue.yt_id


# as I go through the queue, I am going in the order that the songs _will be in_ when I am done.
# so if a song is to be deleted it will be overwritten automatically. So I only need to worry about deleting things at the end of the list.
# so I guess at the beginning I should create a new_length variable to store how long the playlist should be at the end.
# I should also change the published, synced fields maybe to something like next_action.
# but then how do I change the order of the songs in the queue? Or should I just make them have negative position?
# then I can go through all entries and update the playlist and then remove songs... But that also doesn't seems right. I feel like I am trying to avoid querying for the playlist itself to remove the items after a certain point.
# That is the most obvious solution.
# yeah, just truncate the playlist.
from response_data import response_data
results = process_response(response_data)
with open('results.py', 'w') as f:
    f.write("results = " + str(results))

def revoke_permissions_before_commit():
    for user in Profile.objects.all():
        msg = revoke_tokens(user)
        user.revoke_youtube_data()
        print(f"tokens revoked for {user.nickname}")

    


