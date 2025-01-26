from flask import Blueprint, jsonify, session, request
from ..models import *
from ..extensions import db, redis_client, socketio
import datetime
import googlemaps
from ..utlis import *
driver = Blueprint('driver', __name__)
gmaps = googlemaps.Client(key='AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0')
"""
Get all pending booking requests - get_bookings
Accept Booking and start session - accept_booking
Reject Booking and clear session - reject_booking

"""

@driver.route('/driver/bookings', methods=['GET'])
def get_bookings():
    rejected_bookings = session.get('rejected_bookings', [])

    bookings = Order.query.filter(Order.order_status == Order_status.IN_PROGRESS, 
                                  Order.order_id.notin_(rejected_bookings)).all()

    return jsonify([{
        "id": order.order_id,
        "status": order.order_status.value,
        "caller": order.caller.phone_no
    } for order in bookings]), 200

@driver.route("/driver/bookings/<int:id>/accept", methods=["POST"])
def accept_booking(id):
    order = Order.query.filter_by(order_id=id).first()
    if order and order.order_status == Order_status.IN_PROGRESS:
        rejected_bookings = session.get('rejected_bookings', [])
        if id in rejected_bookings:
            rejected_bookings.remove(id)
            session['rejected_bookings'] = rejected_bookings
        
        session['current_order_id'] = id
        session['customer_id'] = order.caller.phone_no
        session['ambulance_id'] = order.ambulance.id
        session['start_time'] = datetime.datetime.utcnow().isoformat()

        return jsonify({
            "message": f"Booking {id} accepted and session started.",
            "start_time": session['start_time']
        }), 200
    return jsonify({"error": "Booking is not available or invalid status."}), 404

@driver.route("/driver/bookings/<int:id>/reject", methods=["POST"])
def reject_booking(id):
    order = Order.query.filter_by(order_id=id).first()
    if order:
        rejected_bookings = session.get('rejected_bookings', [])
        rejected_bookings.append(id)
        session['rejected_bookings'] = rejected_bookings

        session.pop('current_order_id', None)
        session.pop('customer_id', None)
        session.pop('ambulance_id', None)
        session.pop('start_time', None)

        return jsonify({
            "message": f"Booking {id} rejected and is no longer available for you."
        }), 200
    return jsonify({"error": "Booking not found or invalid status."}), 404


''' To be called in the end session endpoint'''
def clear_session():
    session.pop('rejected_bookings', None)
    session.pop('current_order_id', None)
    session.pop('customer_id', None)
    session.pop('ambulance_id', None)
    session.pop('start_time', None)


@driver.route('/driver/update-location', methods=['POST'])
def update_location():
    data = request.json
    order_id = data['order_id']
    ambulance_lat = data['latitude']
    ambulance_lon = data['longitude']

    # Update the ambulance location
    order = Order.query.get(order_id)
    if order and order.ambulance:
        order.ambulance.latitude = ambulance_lat
        order.ambulance.longitude = ambulance_lon
        db.session.commit()

        # Notify traffic lights on the route
        redis_client.publish('ambulance_updates', f"{order_id},{ambulance_lat},{ambulance_lon}")

        socketio.emit('ambulance_update', {
            'order_id': order_id,
            'latitude': ambulance_lat,
            'longitude': ambulance_lon
        })


        return jsonify({"message": "Location updated"}), 200

    return jsonify({"error": "Invalid order or ambulance"}), 404

    
def find_nearest_hospital(caller_lat, caller_long):
    radius = 5  # Initial search radius in kilometers
    step = 5    # Increment step for the radius
    max_radius = 1000
    max_batch_size = 25  # Maximum size of each batch
    nearest_hospital = None
    shortest_distance = float('inf')

    while radius <= max_radius:
        # Filter hospitals within the current radius
        hospitals = [
            hospital for hospital in Hospital.query.all()
            if hospital.latitude and hospital.longitude and
            haversine_distance(caller_lat, caller_long, hospital.latitude, hospital.longitude) <= radius
        ]

        if hospitals:
            # If hospitals are found, split them into batches if the count exceeds max_batch_size
            batches = [
                hospitals[i:i + max_batch_size]
                for i in range(0, len(hospitals), max_batch_size)
            ]

            for batch in batches:
                origins = [(hospital.latitude, hospital.longitude) for hospital in batch]
                destination = (caller_lat, caller_long)

                # Make the API request with the current batch of hospitals
                result = gmaps.distance_matrix(origins=origins, destinations=[destination], mode='driving')
                if result['status'] == 'OK':
                    # Iterate through all the distances in the result
                    for i, element in enumerate(result['rows'][0]['elements']):
                        if element['status'] == 'OK':
                            distance = element["distance"]['value']
                            if distance < shortest_distance:
                                shortest_distance = distance
                                nearest_hospital = batch[i]

            break  # Exit the loop once we find the nearest hospital

        radius += step

    return nearest_hospital


@driver.route('/ambulance/nearest_hospital', methods=['POST'])
def find_nearest_hospital_and_route():
    data = request.json
    ambulance_lat = data.get('latitude')
    ambulance_long = data.get('longitude')

    if not ambulance_lat or not ambulance_long:
        return jsonify({"message": "latitude and longitude are required!"}), 400

    # Find the nearest hospital from the ambulance's current location
    nearest_hospital = find_nearest_hospital(ambulance_lat, ambulance_long)

    if not nearest_hospital:
        return jsonify({"message": "No available hospital found nearby!"}), 404

    # Generate the route from the ambulance to the nearest hospital
    hospital_route_details = get_route_with_directions(
        ambulance_lat, ambulance_long,
        nearest_hospital.latitude, nearest_hospital.longitude
    )
    if hospital_route_details is None:
        return jsonify({"message": "No route generated to hospital!"}), 400
    
    

    # Return the nearest hospital details and the route information
    return jsonify({
        "hospital_name": nearest_hospital.name,
        "hospital_id": nearest_hospital.id,
        "route": hospital_route_details["route"],
        "duration": hospital_route_details["duration"],
        "distance": hospital_route_details["distance"]
    }), 200