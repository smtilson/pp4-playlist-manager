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
Responsiveness was tested on Chrome, Edge, and Firefox. 

### Account Sign up, Login, Logout
I used All-auth to handle sign up, login, and logout. 

### Navigation
Logged in Navigation bar desktop, all links work
footer links tested, they work
login link from sign up page works
not authenticated desktop navigation works

mobile navigation bar?

### Account 
Login works
signout works
sign in link from
Sign up prevents users with same email from signing up
sign up prevents problematic passwords (too short, too similar, too common)
sign up works

### Queue CRUD
Create Queue works and redirects to edit page

add song works
up and down work
swap works

### youtube
publish works
sync adds songs and reorders songs
sync removes songs

### share
share to authentivcated 
guest sign in worked
buttons hidden to non owners

There is an issue with buttons in control panel spacing.
Meg didn't realize that the link would take her to the edit page of the queue, add edit button next to play and share.

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