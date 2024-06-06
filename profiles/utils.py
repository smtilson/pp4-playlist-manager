from .models import Profile
import json


def get_user_profile(request):
    user = Profile.objects.filter(id=request.user.id).first()
    return user