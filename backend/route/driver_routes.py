from flask import Blueprint, jsonify, session
from ..models import *
from ..extensions import db
import datetime

driver = Blueprint('driver', __name__)

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
        