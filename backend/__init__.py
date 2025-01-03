from flask import Flask
from .extensions import db

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/ambulance_monitoring' #if you have used any other db name, changing here alone would suffice
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)    #coupling our app with db now to avoid circular import error

  return app
