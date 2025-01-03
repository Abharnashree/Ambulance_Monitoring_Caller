from app import app, db
from schemas import Ambulance, Caller, Order

@app.route("/init_db_with_dummy_data", methods=['POST'])
def initDB():
  with app.app_context():
    db.create_all()
    caller1 = Caller("1234567890")
    caller2 = Caller("0987654321")
    amb1 = Ambulance(1, "Basic life support")
    amb2 = Ambulance(2, "Advanced life support")
    order1 = Order(1, amb1, caller1)
    order2 = Order(2, amb1, caller2)
    order3 = Order(3, amb2, caller1)
    db.session.add_all([amb1, amb2, caller1, caller2, order1, order2, order3])
    db.session.commit() 
  return "added"