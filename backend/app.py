from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/sample' #if you have used any other db name, changing here alone would suffice
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from admin.add_ambulance import add_ambulance
from admin.init_db_with_dummy_data import initDB
from admin.update_ambulance import update_ambulance

app.add_url_rule('/admin/add_ambulance', view_func=add_ambulance, methods=['POST'])
app.add_url_rule('/admin/init', view_func=initDB, methods=['POST'])
app.add_url_rule('/admin/update_ambulance/<int:ambulance_id>', view_func=update_ambulance, methods=['PUT'])

if __name__ == "__main__":
  app.run(debug=True)
