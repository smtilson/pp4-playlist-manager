# Testing YouTube DJ
This document addresses the testing that was done on YouTube DJ.

Table of contents

- Manual Testing
- Automatic Testing
- Validation
- Bugs

## Manual Testing
Extensive manual testing was done throughout the development of this project.

### Responsiveness
Responsiveness was tested with Chrome, Edge, and Firefox. (It doesn't look as good in Edge, the borders of the containers is wonky.)

### Account Sign up, Login, Logout
I used All-auth to handle sign up, login, and logout. The below verifies that the user authentication features function properly.

| Feature                    | Action                                                                                 | Expected Result                                                                   | Success |
| -------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------- |
| Sign in form               | click on signup link                                                                   | taken to signup form                                                              | yes     |
| Secure Password validation | Filled out form with weak password, non-matching passwordsd, and/or non-email address  | Sign up refused and appropriate feedback given                                    | Yes     |
| Account Signup             | Filled out sign up form with valid data and clicked Sign up button                     | User profile created with those credentials                                       | Yes     |
| Password validation        | Filled out form with incorrect password                                                | Receive feedback stating password is incorrect                                    | Yes     |
|                            |                                                                                        |                                                                                   |         |
| Login form                 | Click on login link                                                                    | Taken to login form                                                               | Yes     |
| Account Login              | Filled out form with valid credentials, clicked Sign In button                         | Logged in as user                                                                 | Yes     |
| Account Login              | Filled out form with valid credentials, checked Remember Me box,clicked Sign In button | Logged in as user, remain logged in when next visiting site after closing browser | Yes     |
|                            |                                                                                        |                                                                                   |         |
| Logout                     | Clicked signout button                                                                 | Logged out of site                                                                | Yes     |


### Navigation
The automated testing checks that the urls take users to the appropriate place depending on: authentication status, guest status, and session data. The below tests that the links "physically" work

| Feature                          | Action                               | Expected Result                                   | Success |
| -------------------------------- | ------------------------------------ | ------------------------------------------------- | ------- |
| Expandable Nav for small devices | Use a small device                   | See burger icon                                   | Yes     |
| Dropdown nav menu                | Click burger icon                    | Menu dropsdown                                    | Yes     |
| Dropdown nav menu                | Click burger icon, menu expanded     | Menu collapses                                    | Yes     |
| Navbar on larger devices         | Use a 768px screen or wider          | See a Navbar menu along the top                   | Yes     |
|                                  |                                      |                                                   |         |
| Auth. User Nav menu              | Look at nav menu while logged in     | See links Home, Logout, Profile, and Create Queue | Yes     |
| Unauth. User Nav menu            | Look at nav menu while not logged in | See links Home, Login, Sign up                    | Yes     |
| Guest Nav menu                   | Look at nav menu as guest            | See Links Edit Queue, Login, Sign up              | Yes     |
|                                  |                                      |                                                   |         |
| Home link                        | Click Home link in nav menu          | Taken to landing page.                            | Yes     |
| Edit Queue link                  | Click Edit Queue link in nav menu    | Taken to Edit page for associated queue           | Yes     |
| Sign up link                     | Click Sign up link in nav menu       | Taken to Sign up page                             | Yes     |
| Login link                       | Click login link in nav menu         | Taken to login page                               | Yes     |
| Logout link                      | Click logout link in nav menu        | Taken to logout page                              | Yes     |
| Profile link                     | Click profile link in nav menu       | Taken to profile page                             | Yes     |
|                                  |                                      |                                                   |         |
| Footer Links                     | Click on Footer YouTube link         | Open YouTube in a new tab                         | Yes     |
|                                  | Click on Footer YTMusic link         | Open YTMusic in a new tab                         | Yes     |

### YouTube Authorization
The automated testing verifies that the backend stores the data properly. The following verifies that authentication is really acquired. This is done through checking that Publish, Unpublish, and Sync work properly below.

| Feature                  | Action                                                    | Expected Result                                        | Success |
| ------------------------ | --------------------------------------------------------- | ------------------------------------------------------ | ------- |
| Authorize YouTube Access | Click Give YouTube DJ permissions and follow instructions | Gives write permissions to YouTube account             | Yes     |
| Revoke YouTube Access    | Click Revoke Credentials                                  | Credentials wiped from the system and notified of this | Yes     |
| Deny Authorization       | Click Give YouTube DJ permissions and deny authorization  | Msg displayed stating what happened                    | Yes     |

### YouTube Interaction
This tests how Publish, Unpublish and Sync interact with YouTube.
| Feature            | Action                                                   | Expected Result                                                                                         | Success |
| ------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------- |
| Publish to YouTube | Click Publish button                                     | Creates playlist on YouTube with videos in correct order. Publish button disappears. Unpublish appears. | Yes     |
| Unpublish          | Click Unpublish button                                   | Opens "Are you sure?" modal                                          | Yes     |
|                    | Click Unpublish button in modal | Deletes YouTube playlist. Unpublish disappears, Publish appears | Yes 
| Sync with Youtube  |                                                          |                                                                                                         |         |
| after Add          | Click Sync button after adding an entry                  | Entry is added on youtube playlist at the end                                                           | Yes     |
| after Remove       | Click Sync button after removing entry                   | Entry is removed from the playlist and positions are adjusted accordingly                               | Yes     |
| after Move         | Click Sync button after changing the position of entries | Playlist is reordered to match the queue                                                                | Yes     |

### Queue CRUD
This tests that the buttons for manipulating queues internally function as expected. This is also verified by automatic testing.

| Feature      | Action                                                         | Expected Result                                                      | Success |
| ------------ | -------------------------------------------------------------- | -------------------------------------------------------------------- | ------- |
| Create Queue | Fill out form and click Create Queue button                    | Redirected to Edit Queue page for new queue                          | Yes     |
| Delete       | Click Delete button                                            | Opens "Are you sure?" modal                                                        | Yes     |
|               | Click Delete button in modal | Deletes queue | Yes |
| Add Entry    | Click Add button next to search result                         | Adds search result to queue at the end                               | Yes     |
| Remove Entry | Click Remove button next to entry                              | Opens "Are you sure?" modal                   | Yes     |
|               | Click Remove button in modal | Entry is removed from list of entries in the queue| Yes|
| Move Entries |                                                                |                                                                      |         |
| Up           | Click Up button                                                | Entry swaps places with entry above (if possible, otherwise nothing) | Yes     |
| Down         | Click Down buttons                                             | Entry swaps places with entry below (if possibile, otherwise nothing | Yes     |
| Swap         | Enter a new position in the range listed and click Swap button | Entry swaps positions with entry in given position                   | Yes     |


### Other features
This is a collection of other features that were tested. Note that Share is extensively tested in the testing of gain_access and redirect_action.

| Feature               | Action                                             | Expected Result                                                | Success |
| --------------------- | -------------------------------------------------- | -------------------------------------------------------------- | ------- |
| Different permissions | Look at Edit Queue page as a non-owner             | Only see Refresh and play buttons                              | Yes     |
| Refresh               | Click Refresh button                               | Edit page refreshes and reflects changes other users have made | Yes     |
| Search                | Enter text into Search field and Hit Search button | Search results from youtube are displayed                      | Yes     |
| Share                 | Send link to friend and then click on it           | Taken to Guest Sign In page                                    | Yes     |
| Play on YouTube       | Click Play on YouTube button                       | Opens link to playlist on YouTube in new tab                   | Yes     |


## Automatic Testing
I used the Django testing framework to test the views. I made use fo the Mock package from Unittest.

I did not write automated tests for user creation, login, and signout as this was handled by All-Auth, but I did manually test these functions as documented above.

The main purpose of this testing was to see if users were directed to the correct page based on their authentication status and permissions. Due to an inability to get Django sessions to function more kindly inside the testing framework, whenever I needed to use session data, I was unable to use the assertRedirect method of TestCase. This meant that I didn't have access to the whole redirect chain, only the first redirect. It explains some discrepancies in the style of tests. I also only tested messaging when it was the only way to check if a certain action had taken place. Otherwise, messages were tested manually.

I checked each branch of each view to see if it behaved as expected. This caused me to rethink some of my code and improve it, in my opinion.

## Validation

### Python
I used flake8 to validate my Python code. I ran flake8 on:
the files
- utils.py
- mixins.py
the directories
- yt_query
- yt_auth
- queues
- profiles
- errors
- pp4_youtube_dj

I did not address the following errors for the stated reason:

1. I did not address any issues that showed up in any of Django's migration files. They were usually that the line was too long.

2. "F401 'env' imported but unused," It is used, but flake8 can not detect that.

3. "E501 line too long" for lines in the settings file of the man app. These involved package names and I didn't want to split them up.

### JavaScript
I used JSHint to validate my JavaScript.

I got the following errors that I did not address:
1. 'async functions' is only available in ES8 (use 'esversion: 8').

2. `position`, `positionDiv`, `positionSpan`, and `swapInputs` are undefined. They are well-defined but JSHint can not verify that.

### CSS
I used W3C Jigsaw to validate my CSS, no errors were found.

### HTML
I used W3C's Markup validator to validate my HTML. I copied the source from chrome for the following pages and pasted it into the validator. 
- Landing page
- Create Queue
- Profile
- Edit Queue
- Guest sign in
- Sign up
- Login
- Logout

There were errors from certain nesting of element tags that isn't allowed, but these were fixed. There were warning about using h2-h6 at the beginning of section elements. I used sections for organizational purposes, to distinguish from divs, and so I ignored this warning.



## Bugs
I used the Kanban board to document bugs that I encountered during development. I did not list every time something seemed to be off in position. I have documented these bugs and their fixes below.

### Bugs Addressed

- Bug: The superuser was unable to log in due to a CSRF token issue. There is a long error message that is in the bug report on GitHub.

Fix: I found a [StackOverflow answer](https://stackoverflow.com/questions/10388033/csrf-verification-failed-request-aborted) that addressed the issue. The solution was to add a list of trusted origins to the settings file.

- Bug: When obtaining credentials using Oauth, the operation stalled at the last step and would not complete.

Fix: This ended up happening because I was using Gitpod. The problem disappeared completely when I started using my local machine as the development environment.

- Bug: Getting 302 status code instead of 200 when trying to revoke tokens.

Fix: I needed to import the requests library in order to handle part of the procedure.

- Bug: There were too many credential objects being created.

Fix: The code was just creating new credential objects instead of updating the existing one. The code was easy to fix. The methods set_credentials was implemented to address this.

- Bug: The up and down buttons for moving entries on the Edit Queue page weren't working correctly. The down button wasn't moving the entry and the up button was moving it up two spots.

Fix: I missed some instances of some attributes when refactoring. Being careful was enough to spot the errors.

- Bug: Delete button disappeared after syncing.

Fix: Carefully inspecting the template logic in the control panel section fixed the issue.

- Bug: Sync was sending invalid positions for playlist items to YouTube.

Fix: I was storing positions inappropriately earlier. I fixed this but didn't change the initial assignment of the position. It was easily addressed.

- Bug: The search stopped working. I was searching each time the page reloaded which used too many PAI resources. I tried to fix this and broke search completely.

Fix: The value I was setting `recent_search` to was Falsy for some reason. Changing this fixed the issue.

- Bug: Move up button on queue entries not working.

Fix: The function name I was using was already in use by Django. There was also a logical issue. Changing from </> to <=/>= addressed the logical issue. For the other I simply changed the name of the method.

- Bug: Creating Queue throws JSON non-serializeable error.

Fix: I was attempting to attach a queue object to a session, and that was causing this error. I instead used a to_dict method. I believe now I just use the queue's id.

- Bug: Adding entries to queue did not increase its length.

Fix: This was occurring when I was increasing the length manually, when adding entries, as opposed to referencing `queue.entries.all()`. The initial issue was that I had not copied the relevant code to the view. Since then, I have switched to using `queue.entries.all()`.

- Bug: When trying to log in a super user an exception was thrown saying: "'Manager' object has no attribute 'get_by_natural_key' error in Django?"

Fix: I used an article to help build my custom user model. I thought the manager code was superfluous so I deleted it. It was necessary and adding it back addressed this error.

- Bug: After sign in of a new account, there is an error because the profile object doesn't exist yet.

Fix: The issues was related to the creation of the credentials object. I let the credentials object be null at the time of profile creation. I then add default credentials when they first visit the profile page if they do not have any.

- Bug: Signout link in navbar is not working.

Fix: This was from when my account related pages where inheriting from the default all-auth base, not my base.html template. Adjusting this addressed the issue.

Bug: After access token has expires the refresh process is failing because an exception is being thrown.

Fix: The issue was cuased by translating between my credentials object and Googles Credentials object. Because I was going from JSON to a dictionary to a field in a database, then back to a dict then a google credentials instance, some extraneous characters were introduced. In particular, the scopes value of `["http://..."]` becomes `'["http://..."]'`, and then some extra characters get introduced. I changed the value being passed to my method which produces an instance of the google credentials object.

- Bug: I was getting "too many redirect" errors. I added some logic to try and catch bad responses. I was not careful enough when doing this.

Fix: Carefully fixing the logic of the views addressed this.

- Bug: When attempting to move entries around, the actual entry changes. This appears to be rectified if the page is refreshed, so it is an issue with the JS function.

Fix: In the JS file, I hardcoded the domain. So it was fetching data from the wrong backend. Now, JS gets the domain from the window object.

- Bug: None of the movement buttons are working on the deployed site.

Fix: It was similar to the above. And then there was a redirect that was getting triggered because the request object that fetch gives to django is an anonymous user and so it will always trigger the user!=owner condition. Removed that redirect from the swap view. Also added headers to the fetch requests and changed the URL for the view since the queue id is not relevant. Then there was the issue of static files being disabled.

- Bug: With the deployed and local versions of the app, the redirect uri isn't matching.

Fix: I changed how the redirect uri is set so it now depends on some environment variables.

- Bug: The position buttons are not appearing for a queue owner.

Fix: Adjusted logic in the template.

- Bug: When a guest visits the edit queue page, owner buttons are appearing.

Fix: Adjust the logic in the template.

- Bug: Publish was throwing an error.

Fix: The user didn't yet have tokens. I adjusted the logic in the template so the button is hidden in that case. Error handling has also been added on the back end to catch this.

- Bug: Search is throwing an error on the deployed site.

Fix: Removed the quotes around the value of the YOUTUBE_API_KEY config var on Heroku.

- Bug: When I remove an entry from the queue it should cause the queue to no longer register as synced.

Fix: I changed which iterator is used t determine if the queue is synced or not.

- Bug: When I have published a queue and then add an entry and sync it, the new song is added at the end.

Fix: Sync did not yet remove items from the playlist. Implementing Sync completely fixed this bug.

- Bug: Two entries on the same playlist had the same position.

Fix: I added a resort method which is called and prevents this from persisting.


### Bugs Left in
The following bugs are things that were left in. I was either unable to find a solution because of ability, the underlying technology over which I have no control (see the first Bug listed), or I ran out of time.

1. Bug: When a Queue is synced with a published YouTube playlist, the playlist only reflects these updates after the current video finishes and when the next video begins (check which next video plays, I forgot). 
Reason for leaving in: It involves how YouTube functions, and I do not know how (it may be impossible) to force their playlist to update based on something that my web app does. This may, in fact, not be possible, even if it would be nice.
2. Bug: When revoking authorization/credentials, the web app does not receive a 200 status code, it seems to fail.
Reason for leaving in: Despite the status code not being 200, the credentials become invalid. This was demonstrated through manual testing in two ways. Firstly, I attempted to use those credentials to sync a playlist and received an error due to the credentials being invalid. Secondly, I checked Google's "Third party apps & services" page and did not find pp4-playlist-manager among the authorized apps. YouTube DJ also removes the credentials from its own system, and provides the user with a link to the "Third party apps & services" page to ensure that the credentials have been invalidated. I feel this is sufficient since the app no longer has the ability to modify that users YouTube account.
3. Bug: There are various styling issues. These are due to trying to center various containers "by hand." As mentioned in the ReadMe, my display differs from the standard one and so my guessing at how centered something is using Chrome's DevTools is sometimes off. Due to the use of Bootstrap, the standard fixes do not work as Bootstrap sets certain display styles that don't allow for flexbox.
