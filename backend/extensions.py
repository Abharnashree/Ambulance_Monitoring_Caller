"""
This file will consist of all the loosely coupled dependencies and extentions 
that are required by the Flask app
"""

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO

db = SQLAlchemy()  #initializing db without a flask app
sess = Session()
socketio = SocketIO()