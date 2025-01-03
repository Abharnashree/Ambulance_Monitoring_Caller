"""
This file will consist of all the loosely coupled dependencies and extentions 
that are required by the Flask app
"""

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()  #initializing db without a flask app