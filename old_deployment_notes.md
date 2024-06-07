The key idea of this porject is to make an easy UI for making collaborative playlists on youtube music.

## Deploymment

### This is what I have done so far to deploy the project

#### Setting up Heroku App
1. Log in to Heroku and navigate to your dashboard.
2. Click on the 'New' button in the upper right and select 'Create new app.'
3. Pick a unique name for your App, select the appropriate region, and click 'Create app.'

#### Setting up APIs
1. Go to <a href="https://console.cloud.google.com/">Google Cloud Platform</a>.
2.  Make sure you are logged into the Google account that you want to associate with this project (as opposed to a work account).
3. Open side navigation bar by clicking on the "burger" icon in the upper left.
4. Click on "select a project" and choose "New Project".
5. Enter a project name and click "Create", and select this new project to go to the project page.
6. Select "APIs & Services" from the menu on the left, and then select Library. We will be enabling the Oauth and the Youtube API, youtube music unofficial api.

##### Getting API Keys
1. From your projects dashboard, navigate to "APIs & Services" and then "Credentials."
2. Click on "Create Credentials" and select "OAuth Client ID." Select "Web Application" and an appropriate name, and then scroll down to "Create" and click it.
3. Download the JSON file when prompted.
4. Move this file into the root directory of your project and change its name to oauth_creds.json. These are your Oauth credentials. They will not be pushed to GitHub as the file name is already stored in the .gitignore file.
5. Navigate to "Oauth Consent screen" in the left hand navigation panel.
6. Make sure that under user type "External" is selected. Then scroll down to "Test users" and follow the instructions in order to add the email addresses of users that you would like to be able to test the app.
7. Under "Authorized redirect URI" enter `http://localhost:8080` (should this be changed.)

5. Click on "Library" in the navigation panel on the left and search for Youtube API.
6. Select the YouTube Data API and enable it. Then click on "Create Credentials."
7. Select the Youtube Data API from the dropdown menu as well as "User Data" then click next.
8. Enter your app name or Youtube DJ as well as your email into the respective fields. Click "Save and Continue."
9. Click on "Add or Remove Scopes." Select the scopes "auth/youtube" and "auth/youtube.readonly." Scroll down to "Update" and click on it. Once more, click on "Save and Continue." attention (do I need the read only one?)
10. Under "Oauth Client ID," select "Web Application" and enter a name for your Oauth client.
11. Add `http://localhost:8080` to the "Authorized redirect URI" as well as the address of your heroku app? I am confused by this. and click "Create".
12. If prompted to set up a Oauth consent screen,
--> 6. Make sure that under user type "External" is selected. Then scroll down to "Test users" and follow the instructions in order to add the email addresses of users that you would like to be able to test the app.
--> 7. Under "Authorized redirect URI" enter `http://localhost:8080` (should this be changed.)
Or am I going to use the ytmusic api?
Then download the credentials and store them in root as above.



### These notes are from the django walkthrough project
4. Click on the 'Settings' tab, scroll down to the 'Config Vars' section, and click 'Reveal Config Vars.'
5. Add a key-value pair with key `DISABLE_COLLECTSTATIC` and value `1`.
6. Add a key-value pair with key `DATABASE_URL`and value the database url provided. (If you no longer have access to this, please contact me.)

(should this be a different deployment section)

6. Install a production ready web-server by entering `pip3 install gunicorn~=20.1` into the terminal.
7. Add this to the requirements.txt file with the terminal command `pip3 freeze --local > requirements.txt`.
8. Create a file (without any extension) named 'Procfile' in the root directory of the repository.
9. Add the line `web: gunicorn my_project.wsgi` to this file and save it. Heroku will use this to run our web app.

(should this be a different deployment section)

10. In the `settings.py` file located in the `my_project` directory, change `DEBUG=True` to `DEBUG=False`.
11. While in `settings.py`, append `, '.herokuapp.com'` to the end of the `ALLOWED_HOSTS` list (if there are no other hosts listed, simply add `'.herokuapp.com'`). (it says to remember the comma, but this is only relevant if there are other hosts, right?)

(is this even a deployment step? I guess so since we will deploy from github and need the procfile)

12. Push these changes to GitHub.
13. Navigate to the 'Deploy' tab of your app on Heroku and enable 'Connect to GitHub' in the 'Deployment method' section.
14. Enter the name of the repository for the project in the search box and click 'Search.'
15. Select the repository from the list of search results.
16. Click 'Deploy Branch' to begin a manual deployment of the relevant branch.

(is this a different deployment section?)

17. Scroll up and open the 'Resources' tab.
there are steps about adding eco dynos and making sure there is no db installed yet. The first isn't entirely relevant to this but will be, not sure about the second. The steps are saved in logseq.

Environment variables
18. Create a file called env.py in the root directory. Add
`import os

os.environ.setdefault(
    "DATABASE_URL", >database_url<)`
where you replace `>database_url<` with the database url provided.
(If you no longer have access to this, please contact me.)

static files deployment

19. install `whitenoise~=5.3.0`

20. add `'whitenoise.middleware.WhiteNoiseMiddleware',` to the `MIDDLEWARE`variable in settings.py directly after the SecurityMiddleware from Django.

21. add `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` to settings.py

22. run `python3 manage.py collectstatic`in the terminal

23. ?? check version of python3 with `python3 -v`?? (in my case it was python-3.12.2)

24. copy supported run time closest to yours in https://devcenter.heroku.com/articles/python-support#specifying-a-python-version (in my case it is python-3.12.3)

25. add `runtime.txt` file to root and add the run time version (in my case this is python-3.12.3)

26. git add, commit, and then push these changes to github.

27. got to heroku page for the deployed app. click on settings. scroll down to config vars and remove the key value pair for DISABLE_COLLECTSTATIC

28. then redeploy??

I think the above about collect static can sort of be collapsed, like take out the earlier stuff about collect static as well.

cloudinary set up

29. download required packages for cloudinary api `pip3 install cloudinary~=1.36.0 dj3-cloudinary-storage~=0.0.6 urllib3~=1.26.15` (this will likely be done by just having them install the requirements with pip).

30. sign up to cloudinary

31. go to the dashboard and copy the CLOUDINARY_URL (mine is CLOUDINARY_URL=cloudinary://736759862794426:NIk-OfM7ERFV3NWf9KoSMKxTXlc@djf0ieux6).

32. go to settings and add the following to the list of installed apps. `cloudinary_storage` must be immediately after `django.contrib.staticfiles`, and add `cloudinary` as well.

33. Go to settings in Heroku, Add CLOUDINARY_URL to the config vars.

34. 

