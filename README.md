# YouTube DJ
## YouTube DJ plays all YOUR hits!

The key idea of this project is to make an easy UI for making collaborative playlists on youtube music.

## Table of contents
Introduction
Design
Features
Deployment
Testing

Welcome to YouTube DJ, a webapp designed to enable collaborative YouTube playlist management. I was inspired to design this webapp based on an experience I had this past Easter. During the celebration with my wife's immediate family, we listened to music. This was done by passing around a single phone and having family members select one song at a time. It seemed to me that it would be convenient to have a way for us to all add songs independently via our own devices. This app enables that while allowing the "owner" of the queue to maintain control.


## Features

### Future Directions
There are several different avenues for future development.

1. The implementation of 4 character codes used to share queues instead of links.
2. The easy transition from Guest user to authenticated user. This would mean, in particular, that the queue initial queue that brought the user to the site would be added to their list of collaborative queues automatically.
3. Queue sharing links updating/expiring. That is to say that the link used to share a queue would expire after a certain amount of time.
4. Taking location into account as not all YouTube videos are accessible in all locations.
5. Being able to determine the privacy status of an uploaded playlist. Currently this is set to unlisted.
6. Enabling other user's to have more control over queues, such as the ability to remove entries or reorder them.
7. Enabling syncing of queues with published playlists so that a queue will reflect songs added to the playlist through YouTube.
8. Enable "friends" or "Frequent Collaborators" and browsing features so that you can see what queues other people are working on/have and request permissions to collaborate on them.
9. Enable better "Share" functionality. Right now, one must copy the link associated to the share button. Instead, it would be nice if for mobile devices it opened the share menu and on desktop it copied the address automatically when you clicked it.

Things I would add in the future would be:
addressing the number of results that are returned. Right now I am limited by the apy rate limit.
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

add two cofnig vars, then use the heroku cli to login and write one of them to a specific file. 
heroku run bash -a pp4-playlist-manager
After logging into the app, enter the command `echo ${GOOGLE_CREDENTIALS} > oauth_creds.json` where the value of google credentials is the contents of your local credentials file.

when adding address for the db remove the quotes.

external user, enter your email address


## Testing
Do to the extensive mature of testing on this project, there is a separate document that addresses this portion of the readme, it can be found here: Link
