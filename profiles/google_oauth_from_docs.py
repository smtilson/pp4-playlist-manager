import google.oauth2.credentials
import google_auth_oauthlib.flow


def get_authorization_url():
    ### Step 1: set authorization parameters


    # Required, call the from_client_secrets_file method to retrieve the client ID from a
    # client_secret.json file. The client ID (from that file) and access scopes are required. (You can
    # also use the from_client_config method, which passes the client configuration as it originally
    # appeared in a client secrets file but doesn't access the file itself.)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'oauth_creds.json',
        scopes=['https://www.googleapis.com/auth/youtube'])

    # Required, indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = 'http://localhost:8000/'

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
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