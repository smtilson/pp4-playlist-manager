# Write helper functions for interacting with youtube API
from profiles.models import Profile
from profiles.utils import get_user_profile

def start_session(request) -> 'service':
    user = get_user_profile(request)
    #what type of object is this credentials object?
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=user.credentials)