from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db  
from ..models import Caller 

'''
New column - password is added to Caller model
'''

auth = Blueprint('auth', __name__)


@auth.route('/caller/register', methods=['POST'])
def register():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    phone_number = data['phone_number']
    password = data['password']

    existing_caller = Caller.query.filter_by(phone_no=phone_number).first()
    if existing_caller:
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_caller = Caller(phone_no=phone_number, password=hashed_password)
    db.session.add(new_caller)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@auth.route('/caller/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    phone_number = data['phone_number']
    password = data['password']

    caller = Caller.query.filter_by(phone_no=phone_number).first()
    if not caller:
        return jsonify({'error': 'User not found'}), 404
    if not check_password_hash(caller.password, password):
        return jsonify({'error': 'Invalid password'}), 401

    session['phone_number'] = phone_number

    return jsonify({'message': 'User logged in successfully'}), 200


@auth.route('/caller/logout', methods=['POST'])
def logout():
    if 'phone_number' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    session.pop('phone_number', None)  

    return jsonify({'message': 'Logged out successfully'}), 200
