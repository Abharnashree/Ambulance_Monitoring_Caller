from flask import request, jsonify
from app import db
from schemas import Ambulance

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
