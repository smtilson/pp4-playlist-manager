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

queue_class_fields="""owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="my_queues", default=1)
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
from yt_query.yt_api_utils import YT
from utils import get_secret

me = Profile.objects.all().first()
queue = me.my_queues.all().first()
all_queues = Queue.objects.all()
queue2 = all_queues[1]
playlist_url = "https://www.youtube.com/playlist?list=PLaPvip_wdwX0etylKbQJBY2PmpLkjIBHT"
yt = YT(me)

