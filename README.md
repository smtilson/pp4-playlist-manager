The key idea of this porject is to make an easy UI for making collaborative playlists on youtube music.

## Deployment

### Setting up APIs

#### Setting up Google Cloud platform project
1. Navigate to console.cloud.google.com while logged in to a your (personal) google account.

2. Click on the project selection menu and click "New Project." Enter a project name, select "No organization," and click "Create."


#### Youtube API without Oauth notes
These will likely be irrelevant, but just in case I am taking notes as I set it up.

1. Click on "Library" in the panel on the left. Enter "Youtube Data API" in the search field and hit enter. Then select "Youtube Data API v3" and click "Enable."

2. Click on "Create Credentials." Make sure that "Youtube Data API v3" is selected under "Which API are you using?" Select "Public data" under "What data will you be accessing?" Then click "Next."

3. Copy the API key and save it in your `env.py` file as `ytp_api_key`. Make sure that your `env.py` file is listed in your `.gitignore` file.

4. Will this need to be restricted? Who knows? attention

#### Youtube API with Oauth notes

1. Click on "Library" in the panel on the left. Enter "Youtube Data API" in the search field and hit enter. Then select "Youtube Data API v3" and click "Enable."

2. Click on "Create Credentials." Make sure that "Youtube Data API v3" is selected under "Which API are you using?" Select "User data" under "What data will you be accessing?" Then click "Next."

3. Enter an appropriate app name, user support email, and developer contact information. Click "Save and Continue."

4. Click on "Add or Remove Scopes." Add "youtube" to the filter to narrow down the options. Select ".../auth/youtube.readonly" as well as ".../auth/youtube" and click on "Update" at the bottom of the screen. Click "Save and Continue."

5. Under "Application type," select "Web application." Enter an appropriate name for your Oauth client. Add the relevant URI's for authorized Javascript origins and redirect requests (such as a local address or that of a heroku app). Click "Create."
Make sure that when you add the URIs that you have the trailing slash there appropriately.

6. Copy your client ID and save it in your env.py file. Download the credentials. Save this JSON file in your local repository under the name `oauth_yt_creds.json`.

Request details: redirect_uri=http://localhost:8080/ flowName=GeneralOAuthFlow

external user, enter your email address


