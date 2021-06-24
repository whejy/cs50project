# MY JOURNAL
#### Video Demo:  <URL HERE>
#### Description:
My Journal is a web application that provides a simple way to create and
manage an online journal. My goal is to provide an experience as close as possible to simply
writing on paper. Filenames, dates and storage are managed automatically and a login is not required until after an
entry has been submitted.

The application features a download button that allows users to download to their machine all of their entries at once as a zip file.
Before or after login, the user is able to change the font and choose a background image, with their preferences being stored in the database.
One design choice I have decided against for now is the ability to choose a colour theme for the website. While I believe this would be
possible using JavaScript to link to multiple different CSS files, I think it would take a large amount of time to implement,
particularly to create the different colour palettes. I may come back to implementing such a feature in the future.

"Static" folder contains the CSS and JS file and all of the possible background image choices available to the user.
"Static/temp" is where download files are stored when the user requests to download their journal entries. The files in this folder are
deleted upon being served.
"Templates" folder contains the HTML files, all extended from "layout.html."
"Helpers.py" contains one helper function which requires a login for certain routes in "application.py"