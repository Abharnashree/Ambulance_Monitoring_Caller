# twilio verified test phone number - +917305303307

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import time
import random
from ..extensions import db
from ..models import Caller 
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, session, make_response
import jwt

# Load environment variables
load_dotenv()

auth = Blueprint('auth', __name__)
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))


def generate_otp():
    return ''.join(random.choice('0123456789') for _ in range(6))


def send_otp(twilio_client, phone_number, otp):
    try:
        message = twilio_client.messages.create(
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            body=f'Your OTP is {otp}',
            to=phone_number
        )
        return message
    except TwilioRestException as e:
        return None


@auth.route('/sendOtp', methods=['POST'])
def get_otp():
    if 'phoneNumber' in request.json:
        phone_number = request.json.get('phoneNumber')
        print(request.json)
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        otp = generate_otp()
        message = send_otp(twilio_client, phone_number, otp)
        if message:
            session['otp_code'] = otp
            session['otp_time'] = time.time()

            print('OTP sent')
            return jsonify({"message_sid": message.sid, "status": "OTP sent"})
        else:
            return jsonify({"error": "Failed to send OTP"})
    return jsonify({"error": "Phone number is required"})

@auth.route('/verifyOtp', methods=['POST'])
def verify_otp():
    data = request.json
    code = data.get('verificationCode')
    name = data.get('name')
    phone_number = data.get('phoneNumber')[-10:]
    
    print(f"Received OTP: {code}, Stored OTP: {session.get('otp_code')}")

    if code != session.get('otp_code'):
        return jsonify({"error": "You entered the wrong code!"}), 400

    otp_time = session.get('otp_time', 0)
    if time.time() - otp_time > 120:
        return jsonify({"error": "OTP has expired"}), 400

    caller = Caller.query.get(phone_number)
    if not caller:
        new_caller = Caller(phone_no=phone_number, name=name)
        db.session.add(new_caller)
        db.session.commit()

    # jwt
    token = jwt.encode(
    {
        'phone_number': phone_number,
        'name': name,
    },
    os.getenv("SECRET_KEY"),
    algorithm='HS256'
    )

    return jsonify({"token":token,"status":"success"}),200


@auth.route('/getUser', methods=['GET'])
def get_user():
    user_id = request.cookies.get("user_id")

    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    user = Caller.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"name": user.name, "phone_no": user.phone_no})

