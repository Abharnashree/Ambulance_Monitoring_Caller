from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy
from .extensions import db
from enum import Enum

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
  ambulance = db.relationship('Ambulance', back_populates='attended_victims_association')
  caller = db.relationship('Caller', back_populates='call_requests')

  order_id = db.Column(db.Integer, primary_key=True)
  ambulance_id = db.Column('ambulance_id', db.Integer, db.ForeignKey('ambulance.id'), nullable=False)
  caller_phone_no = db.Column('caller_phone_no', db.String(10), db.ForeignKey('caller.phone_no'), nullable=False)
  date_time = db.Column(db.DateTime, default=datetime.now())
  order_status = db.Column(db.Enum(Order_status), default= Order_status.PENDING)


  def __init__(self, ambulance, caller, date_time=datetime.now(), order_status=Order_status.PENDING):
    self.ambulance = ambulance
    self.caller = caller
    self.date_time = date_time
    self.order_status = order_status

class Ambulance(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
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
  password = db.Column(db.String(255))
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
  call_requests = db.relationship('Order', back_populates='caller')
 
  def __repr__(self):
    return f'<Caller : {self.phone_no}>'
  
  def __init__(self, phone_no, password=None):
        self.phone_no = phone_no
        if password:
            self.password = password