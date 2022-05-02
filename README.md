# MY JOURNAL

Final project for CS50 Introduction to Computer Science with Python.

#### [Demonstration video](https://youtu.be/dInWV_3cA1Y)


#### Description:
My Journal is a web application that provides a way to create and
manage an online journal. My goal is to provide an experience as close as possible to simply
writing on paper. Filenames, dates and storage are managed automatically and a login is not required until after an
entry has been submitted - this being the primary feature I wanted to implement.

The application features both download and delete buttons whose behaviour is tied to a checkbox via JavaScript. The buttons are only
available to be clicked when at least one entry has been selected via the checkbox. Selected entries can be either deleted or downloaded
depending on which button is clicked. If more than one entry is selected for download, a zip file containing all selected entries will
be served to the user. On the backend, the zip file is deleted automatically upon being served. The individual files, stored in "temp",
are deleted upon further navigation of the website or when the user logs out. If the user has clicked the "download entries"
button via the the "delete account" route, all the user's entries will be downloaded at once as a zip file.

Originally I implemented only a "download all" button on the dashboard. After constructing the checkbox feature and allowing
selected entries to be deleted, I realised it would be a better design choice to allow users to select the entries they wanted to download.
To clean my code up I moved the 'downloadentries' function to helpers.py instead and subsequently called the function from within
application.py where it was needed.

Before or after login, the user is able to change the font and choose a background image and their preferences are stored in the database.
The selection boxes for these options are filled via the backend and checked against the submission to prevent user's submitting edited
HTML to the backend.
I have made sure that if a returning user does not change the font or background from default before logging in, that their preferences
are not then set to the default options upon login. In this instance the user's prior preferences will be
loaded. Only if the user interacts with the dropdown menu will their preferences be updated accordingly.

One design choice I have decided against for now is the ability to choose a colour theme for the website. While I believe this would be
possible using JavaScript to link to multiple different CSS files, I think it would take a large amount of time to implement,
particularly to create the different colour palettes. I may come back to implementing such a feature in the future.

"Static" folder contains the CSS and JS file and all of the possible background image choices available to the user.
"Static/temp" is where download files are stored when the user requests to download their journal entries. The files in this folder are
deleted upon being served.
"Templates" folder contains the HTML files, all extended from "layout.html."
"Helpers.py" contains two helper functions. One which enforces a login required for certain routes in "application.py" and the other
which handles download requests.
