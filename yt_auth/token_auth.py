# The code below borrows from the two Corey Schafer YouTube tutorials listed
# in the references as well as the Oauth documentation. Corey used a different
# type of flow, but I found it helpful nonetheless.
from google_auth_oauthlib.flow import Flow
from utils import get_data_from_path
import os
import requests


if os.path.isfile("env.py"):
    import env

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]

LOCAL = eval(os.environ.get("LOCAL"))
if LOCAL:
    REDIRECT_URI = "http://localhost:8000/"
else:
    REDIRECT_URI = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/"


def get_authorization_url():
    """
    Retrieves the authorization URL for the OAuth2 flow.
    No parameters are needed.
    Returns the authorization URL as a string.
    """
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    # The second return value is state, which is not used currently.
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return authorization_url


def get_tokens(authorization_path):
    """
    Retrieves the access and refresh tokens for a user by performing the
    OAuth2 authorization code flow.
    Args: authorization_path (str)
    Returns: google.oauth2.credentials.Credentials
    """
    state = get_data_from_path(authorization_path)[0]
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES,
                                         state=state)
    flow.redirect_uri = REDIRECT_URI
    authorization_response = REDIRECT_URI + authorization_path
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials


# Gotten from the YouTubeAPI documentation
def revoke_tokens(user):
    """
    Revokes the authorization tokens for a given user. This currently never
    returns 200 despite the credentials being invalidated.
    Parameters: user (Profile)
    Returns: status_code: The status code of the token revocation request.
    """
    if not user.has_tokens:
        msg = "This app does not currently have authorization for"\
              f"{user.nickname}"
        return msg
    else:
        credentials = user.google_credentials
        header_content_type = "application/x-www-form-urlencoded"
        requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": credentials.token},
            headers={"content-type": header_content_type},
        )
    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    status_code = getattr(revoke, "status_code")
    return status_code
