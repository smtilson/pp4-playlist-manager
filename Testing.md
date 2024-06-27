# Testing YouTube DJ
This document addresses the testing that was done on YouTube DJ.

Table of contents

- Manual Testing
- Automatic Testing
- Bugs Fixed
- Bugs Left in

## Manual Testing
Extensive manual testing was done throughout the development of this project.

### Responsiveness
Responsiveness was tested on Chrome, Edge, and Firefox. 

### Account Sign up, Login, Logout
I used All-auth to handle sign up, login, and logout. 

### Queue CRUD


## Bugs Left in
The following bugs are things that were left in. I was either unable to find a solution because of ability, the underlying technology over which I have no control (see the first Bug listed), or I ran out of time.

1. Bug: When a Queue is synced with a published YouTube playlist, the playlist only reflects these updates after the current video finishes and when the next video begins (check which next video plays, I forgot). 
Reason for leaving in: It involves how YouTube functions, and I do not know how (it may be impossible) to force their playlist to update based on something that my web app does. This may, in fact, not be possible, even if it would be nice.
2. Bug: When revoking authorization/credentials, the web app does not receive a 200 status code, it seems to fail.
Reason for leaving in: Despite the status code not being 200, the credentials become invalid. This was demonstrated through manual testing in two ways. Firstly, I attempted to use those credentials to sync a playlist and received an error due to the credentials being invalid. Secondly, I checked Google's "Third party apps & services" page and did not find pp4-playlist-manager among the authorized apps. YouTube DJ also removes the credentials from its own system, and provides the user with a link to the "Third party apps & services" page to ensure that the credentials have been invalidated. I feel this is sufficient since the app no longer has the ability to modify that users YouTube account.
3. In the automated testing I could not figure out how to have data persist past the views into the test. For example, in testing the publish view, the queue attribute `yt_id` was an empty string when tested but when printed before the end of the view function, it was not an empty string. 