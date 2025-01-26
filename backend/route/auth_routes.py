# twilio verified test phone number - +917305303307

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import time
import random
from dotenv import load_dotenv

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
    if 'verificationCode' in request.json:
        code = request.json.get('verificationCode')
        if code == session.get('otp_code'):
            # Check if the OTP is still valid (generated within the last 60 seconds)
            otp_time = session.get('otp_time', 0)
            current_time = time.time()
            if current_time - otp_time <= 120:
                #We can collect user data directly from session
                # user_details = session.get('user_data')
    
                # Collect user data
                # name = request.form.get('name')
                # prn = request.form.get('prn')
                # email = request.form.get('email')
                # branch = request.form.get('branch')
                # phone_number = request.form.get('phone-number')

                # You can now process or store this user data as needed
                # user_data = {
                #     'name': user_details['name'],
                #     'prn': user_details['prn'],
                #     'email': user_details['email'],
                #     'branch': user_details['branch'],
                #     'phone_number': user_details['phone-number']
                # }
                
                # Printing the stored user data
                print("otp verified")
                
                return jsonify({"status": "success"})
            else:
                return jsonify({"error": "OTP has expired"})
        return jsonify({"error": "You entered the wrong code!"})
    return jsonify({"error": "Verification code is required"})

# @auth.route('/caller/logout', methods=['POST'])
# def logout():
#     if 'phone_number' not in session:
#         return jsonify({'error': 'User not logged in'}), 401

#     session.pop('phone_number', None)  

#     return jsonify({'message': 'Logged out successfully'}), 200


# auth = Blueprint('auth', __name__)


# @auth.route('/caller/register', methods=['POST'])
# def register():
#     data = request.get_json()

#     if 'phone_number' not in data or 'password' not in data:
#         return jsonify({'error': 'Phone number and password are required'}), 400

#     phone_number = data['phone_number']
#     password = data['password']

#     existing_caller = Caller.query.filter_by(phone_no=phone_number).first()
#     if existing_caller:
#         return jsonify({'error': 'User already exists'}), 400

#     hashed_password = generate_password_hash(password)
#     new_caller = Caller(phone_no=phone_number, password=hashed_password)
#     db.session.add(new_caller)
#     db.session.commit()

#     return jsonify({'message': 'User registered successfully'}), 201


# @auth.route('/caller/login', methods=['POST'])
# def login():
#     data = request.get_json()

#     if 'phone_number' not in data or 'password' not in data:
#         return jsonify({'error': 'Phone number and password are required'}), 400

#     phone_number = data['phone_number']
#     password = data['password']

#     caller = Caller.query.filter_by(phone_no=phone_number).first()
#     if not caller:
#         return jsonify({'error': 'User not found'}), 404
#     if not check_password_hash(caller.password, password):
#         return jsonify({'error': 'Invalid password'}), 401

#     session['phone_number'] = phone_number

#     return jsonify({'message': 'User logged in successfully'}), 200
