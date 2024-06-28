# Testing YouTube DJ
This document addresses the testing that was done on YouTube DJ.

Table of contents

- Manual Testing
- - Responsiveness
- - Navigation
- Automatic Testing
- - Profiles app views
- - Queues app views
- - Errors app views
- Bugs Fixed
- Bugs Left in

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
| Unpublish          | Click Unpublish button                                   | Deletes YouTube playlist. Unpublish disappears, Publish appears                                         | Yes     |
| Sync with Youtube  |                                                          |                                                                                                         |         |
| after Add          | Click Sync button after adding an entry                  | Entry is added on youtube playlist at the end                                                           | Yes     |
| after Remove       | Click Sync button after removing entry                   | Entry is removed from the playlist and positions are adjusted accordingly                               | Yes     |
| after Move         | Click Sync button after changing the position of entries | Playlist is reordered to match the queue                                                                | Yes     |

### Queue CRUD
This tests that the buttons for manipulating queues internally function as expected. This is also verified by automatic testing.

| Feature      | Action                                                         | Expected Result                                                      | Success |
| ------------ | -------------------------------------------------------------- | -------------------------------------------------------------------- | ------- |
| Create Queue | Fill out form and click Create Queue button                    | Redirected to Edit Queue page for new queue                          | Yes     |
| Delete       | Click Delete button                                            | Deletes Queue                                                        | Yes     |
| Add Entry    | Click Add button next to search result                         | Adds search result to queue at the end                               | Yes     |
| Remove Entry | Click Remove button next to entry                              | Entry is removed from list of entries in the queue                   | Yes     |
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

## Bugs Left in
The following bugs are things that were left in. I was either unable to find a solution because of ability, the underlying technology over which I have no control (see the first Bug listed), or I ran out of time.

1. Bug: When a Queue is synced with a published YouTube playlist, the playlist only reflects these updates after the current video finishes and when the next video begins (check which next video plays, I forgot). 
Reason for leaving in: It involves how YouTube functions, and I do not know how (it may be impossible) to force their playlist to update based on something that my web app does. This may, in fact, not be possible, even if it would be nice.
2. Bug: When revoking authorization/credentials, the web app does not receive a 200 status code, it seems to fail.
Reason for leaving in: Despite the status code not being 200, the credentials become invalid. This was demonstrated through manual testing in two ways. Firstly, I attempted to use those credentials to sync a playlist and received an error due to the credentials being invalid. Secondly, I checked Google's "Third party apps & services" page and did not find pp4-playlist-manager among the authorized apps. YouTube DJ also removes the credentials from its own system, and provides the user with a link to the "Third party apps & services" page to ensure that the credentials have been invalidated. I feel this is sufficient since the app no longer has the ability to modify that users YouTube account.
3. Bug: There are various styling issues. These are due to trying to center various containers "by hand." As mentioned in the ReadMe, my display differs from the standard one and so my guessing at how centered something is using Chrome's DevTools is sometimes off. Due to the use of Bootstrap, the standard fixes do not work as Bootstrap sets certain display styles that don't allow for flexbox.
