from app import app, db
from schemas import Ambulance, Caller, Order

@app.route("/init_db_with_dummy_data", methods=['POST'])
def initDB():
  with app.app_context():
    db.create_all()
    caller1 = Caller("1234567891")
    caller2 = Caller("1987654321")
    amb1 = Ambulance(3, "Basic")
    amb2 = Ambulance(4, "Advanced")
    order1 = Order(6, amb1, caller1)
    order2 = Order(7, amb1, caller2)
    order3 = Order(8, amb2, caller1)
    db.session.add_all([amb1, amb2, caller1, caller2, order1, order2, order3])
    db.session.commit() 
  return "added"