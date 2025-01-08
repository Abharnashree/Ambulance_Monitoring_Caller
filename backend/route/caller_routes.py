from flask import Blueprint, request, jsonify
from ..models import *
from ..extensions import db
import datetime

caller = Blueprint('caller', __name__)

"""
Create Booking - create_booking
Get Booking details with callerno - get_booking_details

"""

@caller.route('/caller/booking', methods=['POST'])
def create_booking():
    data = request.json

    caller_phone_no = data.get('caller_phone_no')
    """
    To-do
    have to assign the nearest ambulance here using 
    google maps api

    """
    ambulance_id = data.get('ambulance_id')
    date_time = data.get('date_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if not caller_phone_no or not ambulance_id:
        return jsonify({"message": "caller_phone_no and ambulance_id are required!"}), 400

    caller = Caller.query.filter_by(phone_no=caller_phone_no).first()
    if not caller:
        return jsonify({"message": f"Caller with phone_no {caller_phone_no} does not exist!"}), 404

    ambulance = Ambulance.query.filter_by(id=ambulance_id, isAvailable=True).first()
    if not ambulance:
        return jsonify({"message": f"Ambulance with ID {ambulance_id} is not available or does not exist!"}), 404

    new_booking = Order(
        ambulance=ambulance,
        caller=caller,
        date_time=datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    )
    new_booking.order_status = Order_status.IN_PROGRESS
    db.session.add(new_booking)

    ambulance.isAvailable = False
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully!",
        "booking_details": {
            "order_id": new_booking.order_id,
            "caller_phone_no": caller_phone_no,
            "ambulance_id": ambulance_id,
            "date_time": new_booking.date_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201

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
