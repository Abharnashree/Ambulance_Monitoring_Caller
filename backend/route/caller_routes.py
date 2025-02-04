from flask import Flask, Blueprint, request, jsonify
from datetime import datetime, timedelta
import googlemaps
from ..models import *
from ..extensions import db, redis_client, socketio
import requests
from flask_socketio import emit, join_room
from twilio.rest import Client
from ..utlis import *
from shapely.geometry import LineString
from geoalchemy2.shape import from_shape
from geoalchemy2.functions import ST_GeomFromText, ST_DWithin, ST_Intersects, ST_Segmentize, ST_Transform, ST_AsText
import polyline


caller = Blueprint('caller', __name__)
gmaps = googlemaps.Client(key='AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0')

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

    route_details = get_route_with_directions(
        nearest_ambulance.latitude, nearest_ambulance.longitude, caller_lat, caller_long
    )

    if route_details is not None:
        print("Route Details in Booking :\n")
        print(route_details) 
    else:
        return jsonify({
            "message":"No Route Details generated",
        }), 400

    ambulance_caller_route = LineString(polyline.decode(route_details['route']))

    # Emit details to both frontends using Socket.IO
    # Send driver details to the caller's frontend
    
    socketio.emit('driver_details', {
        "ambulance_id":nearest_ambulance.id,
        "type": str(nearest_ambulance.type),
        "route": route_details['route'],  
        "duration": route_details["duration"],  
        "distance": route_details["distance"],
        "latitude": nearest_ambulance.latitude,
        "longitude": nearest_ambulance.longitude

    }, to=f"caller-{caller_phone_no}")
    print("Sent details to caller")
    # Send patient location to the ambulance driver's frontend
    socketio.emit('patient_location', {
        "latitude": caller_lat,
        "longitude": caller_long,
        "route": route_details['route'],  
        "duration": route_details["duration"],  
        "distance": route_details["distance"] 
    }, to=f"ambulance-{nearest_ambulance.id}")

    route = ST_Segmentize(from_shape(ambulance_caller_route, srid=4326), 500)

    intersection = TrafficLight.query.filter(
        ST_DWithin(
            ST_Transform(TrafficLight.location, 3857),
            ST_Transform(route, 3857),
            10 # within 10 meters
        )
    ).all()

    new_booking = Order(
        ambulance= nearest_ambulance,
        caller=caller,
        date_time=datetime.now(),
        order_status=Order_status.IN_PROGRESS,
        amb_caller_route = from_shape(ambulance_caller_route, srid=4326)
    )

    proximity = get_proximity(new_booking.amb_caller_route, [traffic_light.location for traffic_light in intersection], 750)
    new_booking.traffic_light_intersection_proximity = proximity

    db.session.add(new_booking)
    nearest_ambulance.isAvailable = False  # Mark ambulance as unavailable
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully!",
        # "booking_details": {
        #     "order_id": new_booking.order_id,
        #     "caller_phone_no": caller_phone_no,
        #     "ambulance_id": nearest_ambulance.id,
        #     "date_time": new_booking.date_time.strftime("%Y-%m-%d %H:%M:%S"),
        #     "route": route_details["route"],  
        #     "duration": route_details["duration"],  
        #     "distance": route_details["distance"],
        # }
    }), 201

# Function to find nearest ambulance
def find_nearest_ambulance(caller_lat, caller_long):
    radius = 5  # Initial search radius in kilometers
    step = 5    # Increment step for the radius
    max_radius = 1000
    nearest_ambulance = None
    shortest_distance = float('inf')
    
    while radius <= max_radius:
        # Filter ambulances within the current radius
        ambulances = [
            ambulance for ambulance in Ambulance.query.filter_by(isAvailable=True).all()
            if ambulance.latitude and ambulance.longitude and
            haversine_distance(caller_lat, caller_long, ambulance.latitude, ambulance.longitude) <= radius
        ]

        if ambulances:
            # If ambulances are found, prepare the origins list for the API request
            origins = [(ambulance.latitude, ambulance.longitude) for ambulance in ambulances]
            destination = (caller_lat, caller_long)
            
            # Make the API request with all ambulances as origins
            result = gmaps.distance_matrix(origins=origins, destinations=[destination], mode='driving')
            print(result)
            if result['status'] == 'OK':
                # Iterate through all the distances in the result
                for i, element in enumerate(result['rows'][0]['elements']):
                    if element['status'] == 'OK':
                        distance = element["distance"]['value']
                        if distance < shortest_distance:
                            shortest_distance = distance
                            nearest_ambulance = ambulances[i]
                    else:
                        print(f"Error for ambulance {ambulances[i].id}: {element.get('status', 'Unknown error')}")
            else:
                print("Google Maps API error:", result.get('error_message'))

            break  # Exit the loop once we find the nearest ambulance

        radius += step

    return nearest_ambulance

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

    # Get caller's location (destination)
    caller_lat = order.caller.latitude      # caller location needs to be stored in the db, otherwise this wont work
    caller_long = order.caller.longitude

# Get last known location and timestamp from Redis
    last_location = redis_client.get(f"ambulance:{ambulance_id}:location")
    last_timestamp = redis_client.get(f"ambulance:{ambulance_id}:last_update_timestamp")

    current_time = datetime.utcnow()

    if last_location and last_timestamp:
        last_lat, last_long = map(float, last_location.decode('utf-8').split(","))
        last_timestamp = datetime.strptime(last_timestamp.decode('utf-8'), "%Y-%m-%d %H:%M:%S")

        # Calculate distance moved since the last update
        distance_moved = haversine_distance(last_lat, last_long, latitude, longitude)

        # If the ambulance not moved more than 10m and it has been more than 3 mins
        if distance_moved < 0.01: 
            time_difference = current_time - last_timestamp
            if time_difference > timedelta(minutes=3):  
                socketio.emit('static_ambulance_report', {
                    "ambulance_id": ambulance_id,
                    "message": "Ambulance has been static for more than 3 minutes."
                }, to=f"dispatcher-{ambulance_id}")  # It should be sent to control static interface

        else:
            
            route_details = get_route_with_directions(latitude, longitude, caller_lat, caller_long)
            if not route_details:
                return jsonify({"message": "Unable to fetch route details!"}), 500

     
            socketio.emit('ambulance_route_update', {
                "ambulance_id": ambulance_id,
                "route": route_details["route"],  
                "duration": route_details["duration"],
                "distance": route_details["distance"]
            }, to=f"caller-{order.caller.phone_no}")

            socketio.emit('ambulance_route_update', {
                "ambulance_id": ambulance_id,
                "route": route_details["route"],
                "duration": route_details["duration"],
                "distance": route_details["distance"]
            }, to=f"ambulance-{ambulance_id}")

    # Cache the updated location in Redis
    redis_client.set(f"ambulance:{ambulance_id}:location", f"{latitude},{longitude}")

    return jsonify({
        "message": "Ambulance location and route updated successfully!",
        "route_details": route_details
    }), 200

# @caller.route('/checking', methods=['POST'])
# def checking():
#     data=request.json
#     caller_phone_no=data.get('caller_phone_no')
#     print("Checking got called")
#     socketio.emit('driver_details', {
#         "message": "This is to see if it works"

#     }, to=f"caller-{caller_phone_no}")
#     return jsonify({
#         "message": "This is to check " + str(caller_phone_no),
#     }), 200


