from flask import Flask
from .extensions import db, sess
from .route.caller_routes import caller
from .route.admin_routes import admin
from .route.esp32_routes import esp32
from .route.driver_routes import driver

def create_app():
  app = Flask(__name__)
  
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ambulance_db'
  #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/ambulance_monitoring'  #if you have used any other db name, changing here alone would suffice
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)    #coupling our app with db now to avoid circular import error

  app.config['SESSION_TYPE'] = 'sqlalchemy'
  app.config['SESSION_SQLALCHEMY'] = db
  app.config['SECRET_KEY'] = 'secret_key'

  sess.init_app(app)

  app.register_blueprint(admin)
  app.register_blueprint(caller)
  app.register_blueprint(esp32)
  app.register_blueprint(driver)

  return app
