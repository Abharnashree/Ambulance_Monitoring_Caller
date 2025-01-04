from flask import Blueprint, request, jsonify, session
from ..models import *
from ..extensions import db
import datetime

esp32 = Blueprint('esp32', __name__)

"""
Start session for request - start_session
Send coordinates to generate map - get_ambulance_map

"""

@esp32.route('/esp32/start', methods=['POST'])
def start_session():
    data = request.json
    customer_id = data.get('customer_id')
    ambulance_id = data.get('ambulance_id')

    # customer_id = '1234567890'
    # ambulance_id = 2
    

    if not customer_id or not ambulance_id:
        return jsonify({"error": "Missing customer_id or ambulance_id"}), 400

    customer = Caller.query.filter_by(phone_no=customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
    if not ambulance:
        return jsonify({"error": "Ambulance not found"}), 404

    session['customer_id'] = customer_id
    session['ambulance_id'] = ambulance_id
    session['start_time'] = datetime.datetime.utcnow().isoformat()

    return jsonify({
        "message": "Session started successfully",
        "start_time": session['start_time']
    }), 201


@esp32.route('/esp32/ambulance-map', methods=['GET'])
def get_ambulance_map():

    if 'customer_id' not in session or 'ambulance_id' not in session:
        return jsonify({"error": "Session not found or expired"}), 404

    customer_id = session['customer_id']
    ambulance_id = session['ambulance_id']

    customer = Caller.query.filter_by(phone_no=customer_id).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
    if not ambulance:
        return jsonify({"error": "Ambulance not found"}), 404

    return jsonify({
        "customer": {
            "phone_no": customer.phone_no,
            "latitude": customer.latitude,
            "longitude": customer.longitude
        },
        "ambulance": {
            "id": ambulance.id,
            "latitude": ambulance.latitude,
            "longitude": ambulance.longitude
        }
    }), 200
