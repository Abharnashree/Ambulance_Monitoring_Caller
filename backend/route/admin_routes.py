from flask import Blueprint, request, jsonify
from ..models import *
from ..extensions import db

admin = Blueprint('admin', __name__)

"""
Add ambulance - add_ambulance
init ambulances - init_db_with_dummy_data
Update ambulance - update_ambulance
"""

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

    ambulances = [Ambulance(x, "basic life support") for x in range(1,100)]
    callers = [Caller(str(x)) for x in range(9_120_356_632,9_999_999_999,1_032_789)]
    orders = [Order(amb, caller) for amb, caller in zip(ambulances[1:100:4], callers[11:555:23])]
    
    db.session.add_all(ambulances)
    db.session.add_all(callers)
    db.session.add_all(orders)

    db.session.commit() 
    return jsonify({
        "ambulances": [ambulance.id for ambulance in ambulances],
        "callers": [caller.phone_no for caller in callers],
        "orders" : [order.order_id for order in orders]
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
