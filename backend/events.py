import random
import time
from flask import request
from flask_socketio import emit, join_room

from .extensions import socketio

# users = {}
rooms = {}
@socketio.on("connect")
def handle_connect():
    print("Client connected!")

@socketio.on("my event")
def handle_message(data):
    print(data)

# Socket.IO event to join rooms
@socketio.on('join_room')
def handle_join_room(data):
    """
    Handles joining rooms for clients.
    Caller joins a room named 'caller-<phone_no>'.
    Ambulance driver joins a room named 'ambulance-<ambulance_id>'.
    """
    room = data.get('room')
    join_room(room)
    print(f"Client joined room: {room}")

'''When using phone's gps, it'll automatically send location updates every few secs
   So the location data is just fetched from driver frontend to backend, and sent to caller frontend'''

@socketio.on('ambulance_location')
def handle_ambulance_location(data):

    print(f"Received location update: {data}")
    emit('ambulance_route_update', data, broadcast=True)   #to caller frontend

