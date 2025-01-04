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
    caller1 = Caller("1234567890")
    caller2 = Caller("0987654321")
    amb1 = Ambulance(1, "Basic life support")
    amb2 = Ambulance(2, "Advanced life support")
    order1 = Order(amb1, caller1)
    order2 = Order(amb1, caller2)
    order3 = Order(amb2, caller1)
    db.session.add_all([amb1, amb2, caller1, caller2, order1, order2, order3])
    db.session.commit() 
    return "added"

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
