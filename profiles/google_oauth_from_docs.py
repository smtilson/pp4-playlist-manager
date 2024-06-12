import google.oauth2.credentials
import google_auth_oauthlib.flow
from utils import get_data_from_path, get_user_profile
from django.shortcuts import reverse
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
]

def get_authorization_url():
    ### Step 1: set authorization parameters


    # Required, call the from_client_secrets_file method to retrieve the client ID from a
    # client_secret.json file. The client ID (from that file) and access scopes are required. (You can
    # also use the from_client_config method, which passes the client configuration as it originally
    # appeared in a client secrets file but doesn't access the file itself.)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'oauth_creds.json',
        scopes=SCOPES)

    # Required, indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = 'http://localhost:8000/'

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    # the second return value is state, which is not used currently.
    authorization_url, _ = flow.authorization_url(
        # Recommended, enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Optional, enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # Optional, if your application knows which user is trying to authenticate, it can use this
        # parameter to provide a hint to the Google Authentication Server.
        #login_hint='hint@example.com',
        # Optional, set prompt to 'consent' will prompt the user for consent
        prompt='consent')

    ### Step 2: redirect user to googles site

    return authorization_url

url_returned_for_sean_account = "http://localhost:8000/?state=g96AagnNUT1sWY4OW0RftFpulDIuTx&code=4/0ATx3LY4gPotL-cs2fHA3miSycYwMuwGi0M2fCg5QCjmuMkAkcixiVsB3tvjiL90EcuDlig&scope=https://www.googleapis.com/auth/youtube.readonly%20https://www.googleapis.com/auth/youtubepartner%20https://www.googleapis.com/auth/youtube"
returned_state = "g96AagnNUT1sWY4OW0RftFpulDIuTx"
returned_code = "4/0ATx3LY4gPotL-cs2fHA3miSycYwMuwGi0M2fCg5QCjmuMkAkcixiVsB3tvjiL90EcuDlig"
"""url = request.META['HTTP_HOST']\
    + request.META['PATH_INFO']\
    + request.META['QUERY_STRING']"""

### Steps 3-4 involve action on googles side of things

### step 5: get tokens
def get_tokens(authorization_path):
    state = get_data_from_path(authorization_path)[0]
    #the below is supposed to verify something?
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'oauth_creds.json',
        scopes=SCOPES,
        state=state)
    #Currently this is hard coded, I am not sure how to make it dynamic.
    flow.redirect_uri = 'http://localhost:8000/'
    #maybe reverse('index')?
    #flow.redirect_uri = request.build_absolute_uri()

    authorization_response = flow.redirect_uri+authorization_path
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials
# Store the credentials in the session.
# ACTION ITEM for developers:
#     Store user's access and refresh tokens in your data store if
#     incorporating this code into your real app.
'''credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes}'''