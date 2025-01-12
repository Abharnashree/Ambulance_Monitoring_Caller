"""
This file will consist of all the loosely coupled dependencies and extentions 
that are required by the Flask app
"""

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO
import redis

db = SQLAlchemy()  #initializing db without a flask app
sess = Session()
socketio = SocketIO(logger=True, engineio_logger=True)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)