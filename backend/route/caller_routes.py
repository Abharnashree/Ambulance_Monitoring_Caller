import googlemaps #use pip install googlemaps if u dont have
from flask import Blueprint, request, jsonify
from ..models import *
from ..extensions import db, redis_client
from datetime import datetime
import math


caller = Blueprint('caller', __name__)
gmaps = googlemaps.Client(key='AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0')


"""
Create Booking - create_booking
Get Booking details with callerno - get_booking_details
"""

@caller.route('/caller/booking', methods=['POST'])
def create_booking():
    data = request.json
    caller_phone_no = data.get('caller_phone_no')
    caller_lat = data.get('latitude')
    caller_long = data.get('longitude')
    """
    To-do
    have to assign the nearest ambulance here using
    google maps api
    """
    if not caller_phone_no:
        return jsonify({"message": "caller_phone_no and is required!"}), 400

    caller = Caller.query.filter_by(phone_no=caller_phone_no).first()
    if not caller:
        return jsonify({"message": f"Caller with phone_no {caller_phone_no} does not exist!"}), 404

    # Find the nearest available ambulance using Google Maps API
    nearest_ambulance = find_nearest_ambulance(caller_lat, caller_long)

    if not nearest_ambulance:
        return jsonify({"message": "No available ambulance found nearby!"}), 404

    # Assign ambulance if a valid ambulance is found
    ambulance = nearest_ambulance

    new_booking = Order(
    ambulance=ambulance,  
    caller=caller,  
    date_time=datetime.now())

    new_booking.order_status = Order_status.IN_PROGRESS 
    '''
    $$ the "type" in ambulance table will work with only 2 values
    "BASIC" and "ADVANCED" and not "basic life support" or "advanced life support"
    '''
    db.session.add(new_booking)
    ambulance.isAvailable = False
    db.session.commit()
    return jsonify({
        "message": "Booking created successfully!",
        "booking_details": {
            "order_id": new_booking.order_id,
            "caller_phone_no": caller_phone_no,
            "ambulance_id": ambulance.id,
            "date_time": new_booking.date_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201


def find_nearest_ambulance(caller_lat, caller_long):
    ambulances = Ambulance.query.filter_by(isAvailable=True).all()
    if not ambulances:
        return None
    
    # Initialize variables to keep track of the nearest ambulance
    nearest_ambulance = None
    shortest_distance = float('inf')
    for ambulance in ambulances:
        if not(ambulance.latitude or ambulance.longitude):
            continue
        ambulance_lat = ambulance.latitude
        ambulance_long = ambulance.longitude


        # This Uses Google Maps Distance Matrix API to calculate the distance
        origin = (caller_lat, caller_long)
        destination = (ambulance_lat, ambulance_long)
        # Calculate distance
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode='driving')
       
        if result['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['value']  # Distance in meters
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_ambulance = ambulance


    return nearest_ambulance


@caller.route('/caller/booking/<string:caller_no>', methods=['GET'])
def get_booking_details(caller_no):

    bookings = Order.query.filter_by(caller_phone_no=caller_no).all()

    if not bookings:
        return jsonify({"message": "No bookings found for this customer!"}), 404

    booking_details_list = []
    for booking in bookings:
        ambulance = booking.ambulance
        booking_details = {
            "order_id": booking.order_id,
            "ambulance_id": ambulance.id if ambulance else None,
            "ambulance_type": ambulance.type if ambulance else None,
            "ambulance_available": ambulance.isAvailable if ambulance else None,
            "date_time": booking.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "caller_phone_no": booking.caller_phone_no
        }
        booking_details_list.append(booking_details)

    return jsonify({"booking_details": booking_details_list}), 200