import os
import requests
import urllib.parse

from os.path import basename
from flask import redirect, flash, render_template, request, session, send_file, after_this_request
from functools import wraps
from zipfile import ZipFile

def downloadEntries(entry):
    """ Downloads entries """

    # Create a text file for each entry and then create a zip file containing those text files,
    # using "counter" as a workaround for duplicate entry titles
    if entry:
        counter=0
        for row in entry:
            counter+=1
            save_path = 'static/temp/'
            file_name = "{} (Entry {}).txt".format(row['title'], str(counter))
            file_entry = "{}\n\n{}".format(row['time'], row['entry'])
            completeName = os.path.join(save_path, file_name)
            zipfilename = "MyEntries.zip"
            with open (completeName, "w") as text_file:
                text_file.write(file_entry)

            with ZipFile(zipfilename, 'a') as zipObj:
              zipObj.write(completeName, basename(completeName))

        # After zip file has been served, remove from server
        @after_this_request
        def remove_file(response):
            os.remove(zipfilename)
            return response


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function