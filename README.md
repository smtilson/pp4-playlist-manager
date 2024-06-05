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

4. Will this need to be restricted?


