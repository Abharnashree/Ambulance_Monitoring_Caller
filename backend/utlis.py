import math
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0')
#This function uses Directions API to get the route 
def get_route_with_directions(origin_lat, origin_long, dest_lat, dest_long):
    try:
        # Request directions from Google Maps API
        result = gmaps.directions(
            origin=(origin_lat, origin_long),
            destination=(dest_lat, dest_long),
            mode="driving",
            traffic_model="best_guess",  # Use real-time traffic data
            departure_time="now"  # Get traffic details for the current time
        )
        print("get_route_with_directions: \n")
        print(result)
        if result and result[0]:
            # Extract route details
            route = result[0]['overview_polyline']['points']  # Encoded polyline for the route
            legs = result[0]['legs'][0]
            duration = legs['duration']['text']  # Total travel time (e.g., "25 mins")
            distance = legs['distance']['text']  # Total distance (e.g., "10.5 km")

            # Get step-by-step directions for turn-by-turn guidance, Let this just be over here for now 
            # steps = []
            # for step in legs['steps']:
            #     directions = step['html_instructions']  # Direction instruction (e.g., "Turn left onto Main St.")
            #     steps.append(directions)

            return {
                "route": route,
                "duration": duration,
                "distance": distance,
                #"steps": steps
            }
        else:
            return None
    except Exception as e:
        print("Error fetching directions:", str(e))
        return None
    
def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points on the Earth
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c