from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy
from .extensions import db
from enum import Enum
from geoalchemy2 import Geometry

'''
New column - password is added to Caller model

'''

class Order_status(Enum):
  PENDING =  "Pending"
  IN_PROGRESS = "In Progress"
  COMPLETED = "Completed"

class Ambulance_type(Enum):
  BASIC = "Basic"
  ADVANCED = "Advanced"

class Order(db.Model):
  # __tablename__ = 'orders'
  ambulance = db.relationship('Ambulance', back_populates='attended_victims_association')
  caller = db.relationship('Caller', back_populates='call_requests_association')

  order_id = db.Column(db.Integer, primary_key=True)
  ambulance_id = db.Column( db.Integer, db.ForeignKey('ambulance.id'), nullable=False)
  caller_phone_no = db.Column( db.String(10), db.ForeignKey('caller.phone_no'), nullable=False)
  date_time = db.Column(db.DateTime, default=datetime.now())
  order_status = db.Column(db.Enum(Order_status), default= Order_status.PENDING)

  amb_caller_route = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=True, default='LINESTRING()')
  caller_hospital_route = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=True, default='LINESTRING()')

  def __init__(self, ambulance, caller, date_time=datetime.now(), order_status=Order_status.PENDING, amb_caller_route='LINESTRING(0 0, 1 0)', caller_hospital_route='LINESTRING(0 0, 1 0)'):
    self.ambulance = ambulance
    self.caller = caller
    self.date_time = date_time
    self.order_status = order_status
    self.amb_caller_route = amb_caller_route
    self.caller_hospital_route = caller_hospital_route

class Ambulance(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  latitude = db.Column(db.Double)
  longitude = db.Column(db.Double)
  isAvailable = db.Column(db.Boolean)
  type = db.Column(db.Enum(Ambulance_type))
  attended_victims_association = db.relationship('Order', back_populates='ambulance')
  attended_victims = association_proxy('attended_victims_association', 'caller')


  def __repr__(self):
    return f'<Ambulance : {self.id}>'

  def __init__(self, id, type):
    self.id = id
    self.type = type  
    self.isAvailable = True

class Caller(db.Model):
  phone_no = db.Column(db.String(10), primary_key=True)
  name = db.Column(db.String(255))
  call_requests_association = db.relationship('Order', back_populates='caller')
  call_requests = association_proxy('call_requests_association', 'ambulance')
 
  def __repr__(self):
    return f'<Caller : {self.phone_no}>'
  
  def __init__(self, phone_no, name):
        self.phone_no = phone_no
        self.name = name

class Hospital(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255))
  latitude = db.Column(db.Double)
  longitude = db.Column(db.Double)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return f'<Hospital : {self.name}>'


class TrafficLight(db.Model):
  id = db.Column(db.String(20), primary_key=True)
  name = db.Column(db.String(255))
  location = db.Column(Geometry(geometry_type="POINT", srid=4326))
  proximity = db.Column(db.Double, default=1000) #1000 meters

  def __init__(self, id, name, location):
    self.id = id
    self.name = name
    self.location = location

  def __repr__(self):
    return f'<Traffic light : {self.location}'