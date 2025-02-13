from flask import Flask
from flask_cors import CORS 
from .extensions import db, sess, redis_client
from .events import socketio
from .views import main
from .route.caller_routes import caller
from .route.admin_routes import admin
from .route.esp32_routes import esp32
from .route.driver_routes import driver
from .route.auth_routes import auth
import threading
import logging
from dotenv import load_dotenv
import os

load_dotenv()  

DB_PASSWORD = os.getenv("DB_PASSWORD")
print("DATABASE PASSWORD",DB_PASSWORD)

def create_app():
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
  
  app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{DB_PASSWORD}@localhost/ambulance_monitoring'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['DEBUG'] = True

  # Initialize SocketIO with CORS
  socketio.init_app(app, cors_allowed_origins="*")  # Allow all origins for socket connections
  logging.getLogger('socketio').setLevel(logging.CRITICAL)  # Suppress socketio logs below WARNING
  logging.getLogger('engineio').setLevel(logging.WARNING)

  db.init_app(app)    #coupling our app with db now to avoid circular import error

  app.config['SESSION_TYPE'] = 'sqlalchemy'
  app.config['SESSION_SQLALCHEMY'] = db
  app.config['SECRET_KEY'] = 'secret_key'

  app.register_blueprint(admin)
  app.register_blueprint(caller)
  app.register_blueprint(esp32)
  app.register_blueprint(driver)
  app.register_blueprint(main)
  app.register_blueprint(auth)

  sess.init_app(app)

  def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('ambulance_updates')
    #TO-DO
    #notify the traffic police on the route
    for message in pubsub.listen():
        if message['type'] == 'message':
            # Broadcast the message to WebSocket clients
            data = message['data']  # Example: "order_id,latitude,longitude"
            socketio.emit('ambulance_update', {'data': data})

  # Start Redis listener in a separate thread
  listener_thread = threading.Thread(target=redis_listener)
  listener_thread.daemon = True
  listener_thread.start()

  return app