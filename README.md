Documentation : https://docs.google.com/document/d/1up91iUYVqkVHMbK-yYIJlsctOlqg2p2JnImRjXyvUT4/edit?usp=sharing

When installing to use, make sure to activate the python virtual env and run 

create python venv with 

py -m venv venv

py -m pip install -r requirements.txt 

so that you have the proper libraries needed to run the web app locally with your own machine as the server

open up python in the terminal and run:

from app import app, db

import models

with app.app_context():

    db.create_all()

to initialise database

Pseudocode can be found in pseudocodes.txt
