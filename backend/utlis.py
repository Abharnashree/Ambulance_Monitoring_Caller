import math
import googlemaps
from sqlalchemy import func, select, text
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.functions import ST_ClosestPoint, ST_LineLocatePoint, ST_LineSubstring, ST_AsText, ST_Length, ST_Transform, ST_GeomFromText
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


def check_proximity(lat, lon, order_id):
    """
    Finds all TrafficLight points within 10 meters of the MultiLineString segment
    that intersects with the given (lat, lon) point in a specific order.

     :param lat: Latitude (double)
    :param lon: Longitude (double)
    :param order_id: Order ID (integer)
    :return: List of dicts with traffic light ID, location, and distance (meters).
    """

    query = text("""
        WITH order_multilines AS (
            -- Get MultiLineString for the given order_id
            SELECT traffic_light_intersection_proximity 
            FROM public.order
            WHERE order_id = :order_id
        ),
        line_segments AS (
            -- Extract each LineString from the MultiLineString
            SELECT ST_GeometryN(traffic_light_intersection_proximity, generate_series(1, ST_NumGeometries(traffic_light_intersection_proximity))) AS segment
            FROM order_multilines
        ),
        intersecting_segments AS (
            -- Filter LineStrings that intersect with the given Point
            SELECT segment FROM line_segments
            WHERE ST_Intersects(segment, ST_SetSRID(ST_MakePoint(:lat, :lon), 4326))
        )

        SELECT t.id,
        t.location,
        ST_Distance(
            ST_Transform(t.location, 9001), 
            ST_Transform(ST_SetSRID(ST_MakePoint(:lat, :lon), 4326), 9001)
        ) AS distance_meters
        FROM public.traffic_light t
        WHERE EXISTS (
            -- Find all TrafficLights within 10 meters of the relevant LineString
            SELECT 1 FROM intersecting_segments s 
            WHERE ST_DWithin(t.location, s.segment, 0.0001)
        )
        ORDER BY distance_meters ASC;
    """)
    
    result = db.session.execute(query, {
        "lat": lat,
        "lon": lon,
        "order_id": order_id
    }).fetchall()

    query = text("""
        WITH order_multilines AS (
            -- Get MultiLineString for the given order_id
            SELECT traffic_light_intersection_proximity 
            FROM public.order
            WHERE order_id = :order_id
        ),
        line_segments AS (
            -- Extract each LineString from the MultiLineString
            SELECT ST_GeometryN(traffic_light_intersection_proximity, generate_series(1, ST_NumGeometries(traffic_light_intersection_proximity))) AS segment
            FROM order_multilines
        ),
        intersecting_segments AS (
            -- Filter LineStrings that intersect with the given Point
            SELECT segment FROM line_segments
            WHERE ST_Intersects(segment, ST_SetSRID(ST_MakePoint(:lat, :lon), 4326))
        ),
        exploded AS (
            SELECT (ST_Dump(traffic_light_intersection_proximity)).geom AS line
            FROM public.order
            WHERE order_id = :order_id
        ),
        filtered AS (
            SELECT line FROM exploded
            WHERE NOT EXISTS (
                SELECT segment FROM intersecting_segments
                WHERE line = segment
            )
        )

        UPDATE public.order
        SET traffic_light_intersection_proximity = (SELECT ST_Collect(line) FROM filtered)
        WHERE order_id = :order_id;
    """)

    db.session.execute(query, {
        "lat": lat,
        "lon": lon,
        "order_id": order_id
    })

    db.session.commit()

    return [{"id": row[0], "location": row[1], "distance_meters": row[2]} for row in result]  # Return a list of dicts
