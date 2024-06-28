from profiles.models import Profile, make_user, GuestProfile
from yt_auth.models import Credentials
from yt_auth.token_auth import revoke_tokens
from queues.models import Queue, Entry, has_authorization
from yt_query.yt_api_utils import YT, process_response
from utils import get_secret
from django.shortcuts import reverse
from queues.tests import TestQueueViews


me = Profile.objects.all().first()

all_queues = Queue.objects.all()
queue = all_queues[len(all_queues)-1]
base_url = "https://www.youtube.com/playlist?list="
playlist_url = "https://www.youtube.com/playlist?list=PLaPvip_wdwX0etylKbQJBY2PmpLkjIBHT"
playlist_id = "PLaPvip_wdwX0Z2KhcrSAZokbY8V_8eIRc"
yt = YT(me)

sample = sample_token ={
            "universe_domain": "googleapis.com",
            "client_id": "secre.client.id.apps.googleusercontent.com",
            "token_uri": "https://oauth2.googleapis.com/token",
            "scopes": "['https://www.googleapis.com/auth/youtube']",
            "refresh_token": "1//refresh_token",
            "account": "",
            "client_secret": "client_secret",
            "has_tokens": True,
            "token": "token",
        }

#sample_video_id1 = entry.video_id
#sample_playlist_id = queue.yt_id

#bad_video = yt.find_video_by_id("12333333333333kasddlmksdfkjasfdnnkwqerrfnksadfknlasdfnlkqwefekjlqwfsdf")
users = Profile.objects.all()

