from flask import Blueprint, request, jsonify, render_template
import requests
from ..models import *
from ..extensions import db
from geoalchemy2.shape import from_shape
from geoalchemy2.functions import ST_GeomFromText, ST_DWithin, ST_Intersects, ST_Segmentize, ST_Transform, ST_AsText
from shapely.geometry import Point
from shapely.wkb import loads
import binascii
from datetime import datetime
from ..utlis import *

admin = Blueprint('admin', __name__)

"""
Add ambulance - add_ambulance
init ambulances - init_db_with_dummy_data
Update ambulance - update_ambulance

"""

@admin.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@admin.route("/test", methods=['GET', 'Post'])
def test():
    print("hello")
    # order = Order.query.filter_by(ambulance_id=230).first()  #update the order id for your testing
    # print(order.amb_caller_route)

    tl = check_proximity(13.03542, 80.25712, 4)
    print(tl)

    return jsonify("done")

@admin.route('/add_ambulance', methods=['POST'])
def add_ambulance():
    data = request.json

    if not data.get('ambulance_id') or not data.get('type'):
        return jsonify({"message": "Missing data for ambulance id or type!"}), 400

    ambulance_id = data.get('ambulance_id')
    ambulance_type = data.get('type')

    existing_ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
    if existing_ambulance:
        return jsonify({"message": "Ambulance with this ID already exists!"}), 409

    ambulance = Ambulance(id=ambulance_id, type=ambulance_type)
    db.session.add(ambulance)
    db.session.commit()

    return jsonify({"message": "Ambulance added successfully!"}), 201


@admin.route('/init_db_with_dummy_data', methods=['POST'])
def init_db_with_dummy_data():
    db.create_all()
    overpass_url = "https://overpass-api.de/api/interpreter"
    CHENNAI_BBOX = "13.0,80.0,13.1,80.3"

    overpass_query = f"""
    [out:json];
    (
    node["amenity"="hospital"]({CHENNAI_BBOX});
    way["amenity"="hospital"]({CHENNAI_BBOX});
    relation["amenity"="hospital"]({CHENNAI_BBOX});
    );
    out center;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})

    ambulances = []
    hospitals = []

    if response.status_code == 200:
        data = response.json()
        i = 1

        #adding a few ambulances and hospitals for testing purpose to reduce the number of element-requests from 
        #google maps api
        for element in data['elements']:
            if i % 46 != 0:
                i += 1
                continue
            ambulance = Ambulance(i, Ambulance_type.BASIC if i%3 != 0 else Ambulance_type.ADVANCED)
            hospital = Hospital(element.get('tags', {}).get('name', 'Unknown'))

            if element['type'] == 'node':
                ambulance.latitude = element['lat']
                ambulance.longitude = element['lon']
                hospital.latitude = ambulance.latitude
                hospital.longitude = ambulance.longitude
            elif 'center' in element:
                ambulance.latitude = element['center']['lat']
                ambulance.longitude = element['center']['lon']
                hospital.latitude = ambulance.latitude
                hospital.longitude = ambulance.longitude
            else:
                continue
            
            ambulances.append(ambulance)
            hospitals.append(hospital)
            i += 1
    else:
        ambulances = [Ambulance(x, Ambulance_type.BASIC) for x in range(1,100)]

        
    callers = [Caller(str(x), "Bob") for x in range(9_120_356_632, 9_999_999_999, 1_032_789)]
    orders = [Order(amb, caller) for amb, caller in zip(ambulances[1:100:4], callers[11:555:23])]

    overpass_query = f"""
    [out:json];
    (
    node["highway"="traffic_signals"]({CHENNAI_BBOX});
    );
    out body;
    """ 

    response = requests.get(overpass_url, params={'data': overpass_query})

    if response.status_code == 200:
        data = response.json()
        for element in data['elements']:
            if element['type'] == 'node':
                lat = element['lat']
                lon = element['lon']
                point_geom = f'POINT({lat} {lon})'  # Create POINT geometry
                traffic_light = TrafficLight(
                    id = element['id'],
                    name = element['tags'].get('name', "Traffic signal"),
                    location=ST_GeomFromText(point_geom, srid=4326)
                )
                db.session.add(traffic_light)


    drivers = [
    Driver("TN01AB1234", "driver123", 46),
    Driver("TN02CD5678", "driver456", 92),
    Driver("TN03EF9012", "driver789", 276),
    Driver("TN04GH3456", "driver234", 414),
    Driver("TN05IJ7890", "driver567", 368),
    Driver("TN06KL1234", "driver890", 460),
    Driver("TN07MN5678", "driver321", 184),
    Driver("TN08OP9012", "driver654", 230),
    Driver("TN09QR3456", "driver987", 138),
    Driver("TN10ST7890", "driver111", 322),
    ]
    
    db.session.add_all(ambulances)
    db.session.add_all(callers)
    db.session.add_all(orders)
    db.session.add_all(hospitals)
    db.session.add_all(drivers)

    db.session.commit() 
    return jsonify({
        "ambulances": [ambulance.id for ambulance in ambulances],
        "callers": [caller.phone_no for caller in callers],
        "orders" : [order.order_id for order in orders],
        "hospitals": [hospital.name for hospital in hospitals],
        "drivers": [driver.number_plate for driver in drivers]
    })

@admin.route('/update_ambulance/<int:ambulance_id>', methods=['PUT'])
def update_ambulance(ambulance_id):
    ambulance = Ambulance.query.get(ambulance_id)
    
    if not ambulance:
        return jsonify({"message": "Ambulance not found!"}), 404
    data = request.json
    ambulance_type = data.get('type')   
    is_available = data.get('isAvailable')

    if ambulance_type:
        ambulance.type = ambulance_type
    if is_available is not None: 
        ambulance.isAvailable = is_available

    db.session.commit()

    return jsonify({"message": "Ambulance updated successfully!"}), 200