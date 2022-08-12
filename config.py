import os
from flask import Flask
from flask_moment import Moment

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO IMPLEMENT DATABASE URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:eudo@localhost:5432/fyyur_artistdb'

SQLALCHEMY_TRACK_MODIFICATIONS=False