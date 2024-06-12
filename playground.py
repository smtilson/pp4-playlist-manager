profile_class_code_raw = """email = models.EmailField(max_length=200, unique=DEBUG)
    name = models.CharField(max_length=200, null=True, blank=True)
    is_superuser = models.BooleanField(default=DEBUG)
    is_staff = models.BooleanField(default=DEBUG)
    is_active = models.BooleanField(default=DEBUG)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    credentials = models.OneToOneField(Credentials,on_delete=models.SET_DEFAULT,null=True,default=Credentials)
    youtube_id = models.CharField(max_length=100,null=True,blank=True, default='')
    youtube_url = models.CharField(max_length=100,null=True,blank=True, default='')""""""
"""

from profiles.models import Profile
from queues.models import Queue, Entry
from yt_query.yt_api_utils import YT

me = Profile.objects.all().first()
yt = YT(me)
wonderwall = yt.search_videos("wonderwall")
one = wonderwall[0]

sample_playlist_id= "PLaPvip_wdwX3VWuno8FBVIceMWcVjToC8"
queues = me.queues.all()
queue1 = queues[0]
for queue in queues:
    queue.youtube_id = ''
    queue.save()