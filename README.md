# MY JOURNAL
#### Video Demo:  <URL HERE>
#### Description:
My project is a web application that provides a simple way to create and
manage a journal. I used Python, Flask, SQL, HTML, CSS and JavaScript.
My priority was simplicity - the primary feature being that the user is able to begin typing right away without
requiring a login. My philosophy was that if a potential feature would make the experience more complicated than simply
writing on paper, it would not be implemented.

The application features a download button that allows users to download to their machine all of their entries at once as a zip file.
On the backend, once these files are served they are auto-deleted.
The user is also able to change the font and choose a background paper image, with their selection being stored in the database.
I debated whether to include the user's font selection in the database, but this would require information to be submitted to the
backend which takes away from the 'smoothness' of the selection because the page then needs to be reloaded.
I also considered storing the selected background image in the database BEFORE the user logs in and then associating it back with
their user_id after log in (in the same way a journal entry is handled before login), but this quickly became very messy and was not
as simple to implement.

"Static" folder contains the CSS file and all of the possible background image choices available to the user.
"Static/temp" is where download files are stored when the user requests to download their journal entries. The files in this folder are
deleted upon being served.
"Templates" folder contains the HTML files, all extended from "layout.html."
"Helpers.py" contains one helper function which just requires a login for certain routes in "application.py"