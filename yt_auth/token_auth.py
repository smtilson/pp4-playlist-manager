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


def get_tokens(authorization_path):
    state = get_data_from_path(authorization_path)[0]
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI
    authorization_response = REDIRECT_URI + authorization_path
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials

# I am guessing that this does not work because of the header
def revoke_tokens(request):
    user = get_user_profile(request)
    if not user.has_tokens:
        return f"This app does not currently have authorization."
    else:
        credentials = google.oauth2.credentials.Credentials(
            **user.credentials.to_dict()
        )

    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        #what is this heaeder supposed to be?
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    print(revoke.__dir__())
    print(revoke)

    status_code = getattr(revoke, "status_code")
    if status_code == 200:
        return "Credentials successfully revoked."
    else:
        return "An error occurred."


def refresh_tokens(request):
    pass
