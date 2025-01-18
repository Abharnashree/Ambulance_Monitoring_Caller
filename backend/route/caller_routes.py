from flask import Flask, Blueprint, request, jsonify
from datetime import datetime
import googlemaps
from ..models import *
from ..extensions import db, redis_client, socketio
import requests
import math 
from flask_socketio import emit, join_room
from twilio.rest import Client


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


    new_booking = Order(
        ambulance= nearest_ambulance,
        caller=caller,
        date_time=datetime.now(),
        order_status=Order_status.IN_PROGRESS
    )
    db.session.add(new_booking)
    nearest_ambulance.isAvailable = False  # Mark ambulance as unavailable
    db.session.commit()

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

    # Emit details to both frontends using Socket.IO
    # Send driver details to the caller's frontend
    socketio.emit('driver_details', {
        "ambulance_id":nearest_ambulance.id,
        "type": str(nearest_ambulance.type),
        "route": route_details["route"],  
        "duration": route_details["duration"],  
        "distance": route_details["distance"] 

    }, to=f"caller-{caller_phone_no}")

    # Send patient location to the ambulance driver's frontend
    socketio.emit('patient_location', {
        # "patient_latitude": caller_lat,
        # "patient_longitude": caller_long,
        "route": route_details["route"],  
        "duration": route_details["duration"],  
        "distance": route_details["distance"] 
    }, to=f"ambulance-{nearest_ambulance.id}")

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


def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points on the Earth
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


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

#This function uses Directions API to get the route 
def get_route_with_directions(origin_lat, origin_long, dest_lat, dest_long):
    try:
        # Request directions from Google Maps API
        result = gmaps.directions(
            origin=(origin_lat, origin_long),
            destination=(dest_lat, dest_long),
            mode="driving",
            traffic_model="best_guess",  # Use real-time traffic data
            departure_time="now"  # Get traffic details for the current time
        )
        print("get_route_with_directions: \n")
        print(result)
        if result and result[0]:
            # Extract route details
            route = result[0]['overview_polyline']['points']  # Encoded polyline for the route
            legs = result[0]['legs'][0]
            duration = legs['duration']['text']  # Total travel time (e.g., "25 mins")
            distance = legs['distance']['text']  # Total distance (e.g., "10.5 km")

            # Get step-by-step directions for turn-by-turn guidance, Let this just be over here for now 
            # steps = []
            # for step in legs['steps']:
            #     directions = step['html_instructions']  # Direction instruction (e.g., "Turn left onto Main St.")
            #     steps.append(directions)

            return {
                "route": route,
                "duration": duration,
                "distance": distance,
                #"steps": steps
            }
        else:
            return None
    except Exception as e:
        print("Error fetching directions:", str(e))
        return None



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
    caller_lat = order.caller.latitude
    caller_long = order.caller.longitude

    # Calculate route details using Directions API
    route_details = get_route_with_directions(latitude, longitude, caller_lat, caller_long)
    if not route_details:
        return jsonify({"message": "Unable to fetch route details!"}), 500

    # Notify both frontends about the updated route
    socketio.emit('ambulance_route_update', {
        "ambulance_id": ambulance_id,
        "route": route_details["route"],  # Encoded polyline for rendering on the map
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

@caller.route('/checking', methods=['POST'])
def checking():
    data=request.json
    caller_phone_no=data.get('caller_phone_no')
    print("Checking got called")
    socketio.emit('driver_details', {
        "message": "This is to see if it works"

    }, to=f"caller-{caller_phone_no}")
    return jsonify({
        "message": "This is to check " + str(caller_phone_no),
    }), 200


