import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.json
    order_id = data['order_id']
    ambulance_lat = data['latitude']
    ambulance_lon = data['longitude']

    # Update the ambulance location
    order = Order.query.get(order_id)
    if order and order.ambulance:
        order.ambulance.latitude = ambulance_lat
        order.ambulance.longitude = ambulance_lon
        db.session.commit()

        # Notify traffic lights on the route
        redis_client.publish('traffic_updates', f"{order_id},{ambulance_lat},{ambulance_lon}")

        return jsonify({"message": "Location updated"}), 200

    return jsonify({"error": "Invalid order or ambulance"}), 404
 