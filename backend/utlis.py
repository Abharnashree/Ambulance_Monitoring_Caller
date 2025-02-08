import math
import googlemaps
from sqlalchemy import func, select, text
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_ClosestPoint, ST_LineLocatePoint, ST_LineSubstring, ST_AsText, ST_Length, ST_Transform
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import substring
from pyproj import Transformer
from .extensions import *
from .models import *
from shapely import wkb

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

def get_proximity(linestring, points, buffer_distance=0.01):

    query = text("""
        WITH input AS (
            SELECT ST_SetSRID(ST_GeomFromEWKB(:linestring), 4326) AS line
        ),
        points AS (
            SELECT ST_SetSRID(ST_GeomFromEWKB(unnest(array[:points_list])), 4326) AS pt
        ),
        segments AS (
            SELECT 
                ST_LineSubstring(line, 
                    GREATEST(ST_LineLocatePoint(line, pt) - (:buffer_distance / ST_Length(line)::float), 0),
                    LEAST(ST_LineLocatePoint(line, pt) + (:buffer_distance / ST_Length(line)::float), 1)
                ) AS segment
            FROM input, points
        )
        SELECT ST_SetSRID(ST_Collect(segment), 4326) AS multilinestring FROM segments;
    """)

    result = db.session.execute(query, {
        "linestring": linestring.data,  # Directly use the WKBElement
        "points_list": [point.data for point in points],    # Pass the list of WKBElement points
        "buffer_distance": buffer_distance
    }).scalar()

    return result  # Returns MultiLineString (WKBElement)
