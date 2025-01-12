from flask import request
from flask_socketio import emit

from .extensions import socketio

# users = {}

@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on("my event")
def handle_message(data):
    print(data)


