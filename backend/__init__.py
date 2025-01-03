from flask import Flask
from .extensions import db
from .route.caller_routes import caller
from .route.admin_routes import admin
from .route.esp32_routes import esp32

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/sample' #if you have used any other db name, changing here alone would suffice
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SECRET_KEY'] = 'secret_key'

  db.init_app(app)    #coupling our app with db now to avoid circular import error
  app.register_blueprint(admin)
  app.register_blueprint(caller)
  app.register_blueprint(esp32)

  return app
