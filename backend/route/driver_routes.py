from flask import Blueprint, jsonify, session, request
from ..models import *
from ..extensions import db, redis_client, socketio
import datetime
import googlemaps
from ..utlis import *
from shapely.geometry import LineString
from geoalchemy2.shape import from_shape
from geoalchemy2.functions import ST_GeomFromText, ST_DWithin, ST_Intersects, ST_Segmentize, ST_Transform, ST_AsText
import polyline
import time

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


@driver.route('/driver/update-location', methods=['POST'])
def update_location():
    data = request.json
    order_id = data['order_id']
    ambulance_lat = data['latitude']
    ambulance_lon = data['longitude']

    # Update the ambulance location
    order = Order.query.get(order_id)
    if order and order.ambulance:
        if(order.ambulance.latitude == ambulance_lat and order.ambulance.longitude == ambulance_lon):
            print('ambulance is stagnant')
            query = text("""
                SELECT t.id FROM public.traffic_light t
                WHERE ST_DWithin(ST_SetSRID(ST_MakePoint(:lat, :lon), 4326), t.location, 0.001)
            """)
            result = db.session.execute(query, {
                "lat" : ambulance_lat,
                "lon" : ambulance_lon
            }).fetchone()

            traffic_id = result[0] if result else None
           
            socketio.emit('ambulance_signal_update', {"order_id" : order.order_id, "signal_id" : traffic_id, "timestamp" : time.time()}, room="dashboard")
        
        query = text("""
            SELECT t.id FROM public.traffic_light t
            WHERE ST_DWithin(ST_SetSRID(ST_MakePoint(:lat, :lon), 4326), t.location, 0.0001)
        """)
        result = db.session.execute(query, {
            "lat" : ambulance_lat,
            "lon" : ambulance_lon
        }).fetchone()

        traffic_id = result[0] if result else None

        if traffic_id is not None:
            socketio.emit('ambulance_signal_crossed', {"order_id" : order.order_id, "signal_id" : traffic_id}, room="dashboard")

        intersecting_traffic_lights = check_proximity(ambulance_lat, ambulance_lon, order_id)
        print(intersecting_traffic_lights)
        
        if(len(intersecting_traffic_lights) > 0):
            print(intersecting_traffic_lights)
            
            for traffic_light in intersecting_traffic_lights:
                timestamp = time.time() + traffic_light.get("distance_meters")/(40*1000/(60*60)) #40kmph
                update = {"order_id" : order_id, "signal_id" : traffic_light.get("id"), "timestamp": timestamp }
                socketio.emit("ambulance_signal_update", update, room="dashboard")

            
        order.ambulance.latitude = ambulance_lat
        order.ambulance.longitude = ambulance_lon
        db.session.commit()

        current_time = datetime.utcnow()
        redis_client.set(f"ambulance:{order_id}:location", f"{ambulance_lat},{ambulance_lon}")
        redis_client.set(f"ambulance:{order_id}:last_update_timestamp", current_time.strftime("%Y-%m-%d %H:%M:%S"))
       
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
    order_id = data.get('order_id')
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
    
    caller_hospital_route = LineString(polyline.decode(hospital_route_details['route']))

    route = ST_Segmentize(from_shape(caller_hospital_route, srid=4326), 0.001) #111m

    intersection = TrafficLight.query.filter(
        ST_DWithin(
            ST_Transform(TrafficLight.location, 3857),
            ST_Transform(route, 3857),
            10 # within 10 meters
        )
    ).all()

    order = Order.query.filter_by(order_id=order_id).first()
    order.traffic_light_intersection = [traffic_light.id for traffic_light in intersection]
    order.caller_hospital_route = from_shape(caller_hospital_route, srid=4326)

    order.traffic_light_intersection_proximity = get_proximity(order.caller_hospital_route, [traffic_light.location for traffic_light in intersection], 0.01)

    db.session.commit()

    # Return the nearest hospital details and the route information
    return jsonify({
        "hospital_name": nearest_hospital.name,
        "hospital_id": nearest_hospital.id,
        "route": hospital_route_details["route"],
        "duration": hospital_route_details["duration"],
        "distance": hospital_route_details["distance"]
    }), 200