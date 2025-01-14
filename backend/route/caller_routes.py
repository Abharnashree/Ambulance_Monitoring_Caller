from flask import Flask, Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import googlemaps
from ..models import *
from ..extensions import db

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
caller = Blueprint('caller', __name__)
gmaps = googlemaps.Client(key='AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@caller.route('/caller/booking', methods=['POST'])
def create_booking():
    data = request.json
    caller_phone_no = data.get('caller_phone_no')
    caller_lat = data.get('latitude')
    caller_long = data.get('longitude')

    if not caller_phone_no:
        return jsonify({"message": "caller_phone_no is required!"}), 400

    # Find the caller
    caller = Caller.query.filter_by(phone_no=caller_phone_no).first()
    if not caller:
        return jsonify({"message": f"Caller with phone_no {caller_phone_no} does not exist!"}), 404

    # Find the nearest available ambulance
    nearest_ambulance = find_nearest_ambulance(caller_lat, caller_long)
    if not nearest_ambulance:
        return jsonify({"message": "No available ambulance found nearby!"}), 404

    # Create the booking
    new_booking = Order(
        ambulance=nearest_ambulance,
        caller=caller,
        date_time=datetime.now(),
        order_status=Order_status.IN_PROGRESS
    )
    db.session.add(new_booking)
    nearest_ambulance.isAvailable = False  # Mark ambulance as unavailable
    db.session.commit()

    # Emit details to both frontends using Socket.IO
    # Send driver details to the caller's frontend
    socketio.emit('driver_details', {
        "driver_name": nearest_ambulance.driver_name,
        "driver_phone": nearest_ambulance.driver_phone,
        "vehicle_number": nearest_ambulance.vehicle_number
    }, to=f"caller-{caller_phone_no}")

    # Send patient location to the ambulance driver's frontend
    socketio.emit('patient_location', {
        "patient_latitude": caller_lat,
        "patient_longitude": caller_long
    }, to=f"ambulance-{nearest_ambulance.id}")

    return jsonify({
        "message": "Booking created successfully!",
        "booking_details": {
            "order_id": new_booking.order_id,
            "caller_phone_no": caller_phone_no,
            "ambulance_id": nearest_ambulance.id,
            "date_time": new_booking.date_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201


# Function to find nearest ambulance
def find_nearest_ambulance(caller_lat, caller_long):
    ambulances = Ambulance.query.filter_by(isAvailable=True).all()
    if not ambulances:
        return None

    nearest_ambulance = None
    shortest_distance = float('inf')

    for ambulance in ambulances:
        if not(ambulance.latitude and ambulance.longitude):
            continue

        # Calculate the distance using Google Maps API
        origin = (caller_lat, caller_long)
        destination = (ambulance.latitude, ambulance.longitude)
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode='driving')
        print(result)
       
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]["distance"]['value']  # Distance in meters
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_ambulance = ambulance
        else:
            print("not ok")

    return nearest_ambulance


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


#This update the screen of the users if any movement is noticed from the driver 
@caller.route('/ambulance/location/update', methods=['POST']) 
def update_ambulance_location():
    data = request.json
    ambulance_id = data.get('ambulance_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not ambulance_id or not latitude or not longitude:
        return jsonify({"message": "ambulance_id, latitude, and longitude are required!"}), 400

    ambulance = Ambulance.query.get(ambulance_id)
    if not ambulance:
        return jsonify({"message": f"Ambulance with ID {ambulance_id} not found!"}), 404

    # Get the active order for this ambulance
    order = Order.query.filter_by(ambulance_id=ambulance_id, order_status=Order_status.IN_PROGRESS).first()
    if not order:
        return jsonify({"message": "No active order found for this ambulance!"}), 404

    # Send the updated location to the caller based on the order
    caller_phone_no = order.caller.phone_no

    # Notify both frontends (caller and ambulance driver) about the ambulance's updated location
    socketio.emit('ambulance_location_update', {
        "ambulance_id": ambulance_id,
        "latitude": latitude,
        "longitude": longitude
    }, to=f"caller-{caller_phone_no}")

    socketio.emit('ambulance_location_update', {
        "ambulance_id": ambulance_id,
        "latitude": latitude,
        "longitude": longitude
    }, to=f"ambulance-{ambulance_id}")

    # Cache the updated location in Redis
    redis_client.set(f"ambulance:{ambulance_id}:location", f"{latitude},{longitude}") #Saving the change cause we might need it later, idk

    # Return success response
    return jsonify({"message": "Ambulance location updated successfully!"}), 200
