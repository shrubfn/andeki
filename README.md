Documentation : https://docs.google.com/document/d/1up91iUYVqkVHMbK-yYIJlsctOlqg2p2JnImRjXyvUT4/edit?usp=sharing

To run in CMD, go to cd (filepath)

When installing to use, make sure to activate the python virtual env and run 

create python venv with 

py -m venv venv

activate venv:

for mac: source venv/bin/activate

windows: \venv\Scripts\activate

py -m pip install -r requirements.txt  (RUN INSIDE VENV)

so that you have the proper libraries needed to run the web app locally with your own machine as the server

open up python in the terminal and run:

from app import app, db

import models

with app.app_context():

db.create_all()

to initialise database

then run app.py

Pseudocode can be found in pseudocodes.txt
