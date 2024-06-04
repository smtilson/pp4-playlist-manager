# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Optional

credentials = None
sean_id = 'CTLP0aZxWx25BZYzbzHjvA'
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly', # given the above, this may not be necessary as well
    'https://www.googleapis.com/auth/youtubepartner' # I don't think this is necessary
    ]

# should I make a credentials class?
# it could do various aspects of validation.
# it could also contain a lot of the below methods.
# maybe, depends on how things work with the database I guess.

# Is this the name/structure I want?
# I guess really, the relevant json file should be returned so it can be passed
# to the ytmusic api.
# is tht the same as the access token?
def grant_access(user_id: str) -> None:
    '''
    user_id: identifies user to locate appropriate records.
    Grants access to modify youtube account of user_id. This is done by
    retrieving previously saved credentials or getting the credentials using the Oauth
    api.
    Returns access token.
    '''
    credentials = None
    if retrieve_credentials(user_id):
        credentials = retrieve_credentials(user_id)
    else:
        credentials = get_credentials(user_id)
    # credentials = retrieve_credentials(user_id) if retrieve_credentials(user_id) else get_credentials(user_id)
    # pass
    return credentials

def save_credentials(user_id: str, access_token,refresh_token) -> Optional[tuple[str]]:
    '''
    user_id: identifies user to locate appropriate save location
    access_token: supplied by oauth api
    refresh_token: supplied by oauth api
    Saves credentials to database.
    Returns: tuple of inputs given without modification
    '''
    print("Saving credentials to database.")
    pass

def get_credentials(user_id: str) -> tuple[str]:
    print("Obtaining credentials from Oauth api.")
    # trying with oatuh_creds first
    flow = InstalledAppFlow.from_client_secrets_file("oauth_yt_creds.json",
                                                 scopes=SCOPES)
    # prompt='consent' should not be necessary
    # authorization_prompt_message='' means that the prompt won't be printed to the console
    flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    credentials = flow.credentials

def retrieve_credentials(user_id: str) -> tuple[str]:
    '''
    user_id: identifies user
    Check database for existing credentials. Checks if access token is still
    valid, if not, uses refresh token to obtain new access token.
    returns credentials with valid acces token.
    '''
    print(f"Attempting to retrieve credentials for user {user_id}.")
    pass
    # have to look them up in the django db somehow
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return credentials

if __name__ == "__main__":
    get_credentials(sean_id)