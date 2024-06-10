from django.db import models
from .yt_api_utils import YT

'''
# Create your models here.
class YTVideo(models.Model):
    pass

    @classmethod
    def find_video_results(cls, user: "Profile", query: str) -> "YTVideo":
        yt = YT(user)
        # I am not sure how to deal with max results
        request = yt.service.search().list(
            part="id,title", type="video", q=query, max_results=25
        )
        response = request.execute()
        #then need to process the response.
        pass
        

class YTPlayList(models.Model):
    pass

class YTSong(models.Model):
    pass
'''