from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flask' #if you have used any other db name, changing here alone would suffice
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
  ambulance = db.relationship('Ambulance', back_populates='attended_victims_association')
  caller = db.relationship('Caller', back_populates='call_requests')

  order_id = db.Column(db.Integer, primary_key=True)
  ambulance_id = db.Column('ambulance_id', db.Integer, db.ForeignKey('ambulance.id'))
  caller_phone_no = db.Column('caller_phone_no', db.String(10), db.ForeignKey('caller.phone_no'))
  date_time = db.Column(db.DateTime, default=datetime.datetime.now())

  def __init__(self, order_id, ambulance, caller, date_time=datetime.datetime.now()):
    self.order_id = order_id
    self.ambulance = ambulance
    self.caller = caller
    self.date_time = date_time

class Ambulance(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
  isAvailable = db.Column(db.Boolean)
  type = db.Column(db.String(20))
  attended_victims_association = db.relationship('Order', back_populates='ambulance')
  attended_victims = association_proxy('attended_victims_association', 'caller')


  def __repr__(self):
    return f'<Ambulance : {self.id}>'

  def __init__(self, id, type):
    self.id = id
    self.type = type  

class Caller(db.Model):
  phone_no = db.Column(db.String(10), primary_key=True)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
  call_requests = db.relationship('Order', back_populates='caller')

  def __repr__(self):
    return f'<Caller : {self.phone_no}>'

  def __init__(self, phone_no):
    self.phone_no = phone_no

caller1 = Caller("1234567890")
caller2 = Caller("0987654321")
amb1 = Ambulance(1, "Basic life support")
amb2 = Ambulance(2, "Advanced life support")
order1 = Order(1, amb1, caller1)
order2 = Order(2, amb1, caller2)
order3 = Order(3, amb2, caller1)


#call this endpoint only once, multiple call_requests with cause a duplicate key error
#if you want to add more dummy data create a new endpoint with differnt keys
@app.route("/init_db_with_dummy_data", methods=['POST'])
def initDB():
  with app.app_context():
    db.create_all()
    db.session.add_all([amb1, amb2, caller1, caller2, order1, order2, order3])
    db.session.commit() 
  return "added"


@app.route("/hi")
def hi():
  return jsonify("hi", 'hello')

@app.route("/hello")
def hello():
  return jsonify({"hello" : "world", "a" : "b"}, {"x" : "y"})


if __name__ == "__main__":
  app.run(debug=True)
