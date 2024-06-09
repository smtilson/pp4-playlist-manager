from profiles.models import Profile
from django.shortcuts import get_object_or_404
import json


def get_user_profile(request):
    # this needs some error handling in case there is no user.
    user = get_object_or_404(Profile, id=request.user.id)
    return user

def empty_dict(dictionary:dict) -> bool:
    return [val for val in dictionary.values() if val]==[]

def get_data_from_path(path:str) -> tuple[str]:
    parts = path.split('&')
    state = parts[0][8:]
    code = parts[1][5:]
    scope = parts[2][6:].split('%20')
    return (state,code,scope)


    