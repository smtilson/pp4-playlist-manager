import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow
from .utils import get_data_from_path, get_user_profile
from django.shortcuts import reverse
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]

# this should be changed to an environment variable
REDIRECT_URI = "http://localhost:8000/"


def get_authorization_url():
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    # the second return value is state, which is not used currently.
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return authorization_url


url_returned_for_sean_account = "http://localhost:8000/?state=g96AagnNUT1sWY4OW0RftFpulDIuTx&code=4/0ATx3LY4gPotL-cs2fHA3miSycYwMuwGi0M2fCg5QCjmuMkAkcixiVsB3tvjiL90EcuDlig&scope=https://www.googleapis.com/auth/youtube.readonly%20https://www.googleapis.com/auth/youtubepartner%20https://www.googleapis.com/auth/youtube"
returned_state = "g96AagnNUT1sWY4OW0RftFpulDIuTx"
returned_code = (
    "4/0ATx3LY4gPotL-cs2fHA3miSycYwMuwGi0M2fCg5QCjmuMkAkcixiVsB3tvjiL90EcuDlig"
)
"""url = request.META['HTTP_HOST'] \
    + request.META['PATH_INFO'] \
    + request.META['QUERY_STRING']"""

def get_tokens(authorization_path):
    state = get_data_from_path(authorization_path)[0]
    # the below is supposed to verify something?
    flow = Flow.from_client_secrets_file(
        "oauth_creds.json", scopes=SCOPES, state=state
    )
    # Currently this is hard coded, I am not sure how to make it dynamic.
    flow.redirect_uri = "http://localhost:8000/"
    # maybe reverse('index')?
    # flow.redirect_uri = request.build_absolute_uri()

    authorization_response = flow.redirect_uri + authorization_path
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials


# Store the credentials in the session.
# ACTION ITEM for developers:
#     Store user's access and refresh tokens in your data store if
#     incorporating this code into your real app.
"""credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes}"""
