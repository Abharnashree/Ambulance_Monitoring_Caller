import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { Marker, Polyline } from 'react-native-maps';
import MapView from 'react-native-maps';
import polyline from '@mapbox/polyline';
import io from 'socket.io-client';
import BottomSheetComponent from '../components/BottomSheetComponent';

const AmbTrack = ({route}) => {
  const { driverDetails, userLocation } = route.params;
  console.log("The driverDetail : ----------------------------");
  console.log(driverDetails);
  console.log("The userCLocation : ----------------------------");
  console.log(userLocation);
  const [ambulanceDetails, setAmbulanceDetails] = useState({
    ambulance_id: driverDetails.ambulance_id,
    distance: driverDetails.distance,
    duration: driverDetails.duration,
    route: driverDetails.route,
    type: driverDetails.type,
    latitude: driverDetails.latitude,
    longitude: driverDetails.longitude,
  });
  useEffect (() => {
    console.log("The ambulanceDetails update from USE EFFECTTT : ----------------------------");
    console.log(ambulanceDetails);
  }, [ambulanceDetails]);

  // const userCLocation = {
  //   latitude: 11.934842145143234,
  //   longitude: 79.78588598212839,
  // };

  const [decodedPolyline, setDecodedPolyline] = useState([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const bottomSheetRef = useRef(null);
  const socket = useRef(null);

  // Decode polyline whenever the route changes
  useEffect(() => {
    if (ambulanceDetails.route) {
      console.log(" Decoding new polyline:", ambulanceDetails.route);
      try {
        const decoded = polyline.decode(ambulanceDetails.route).map((coord) => ({
          latitude: coord[0],
          longitude: coord[1],
        }));
        setDecodedPolyline(decoded);
      } catch (error) {
        console.error(" Error decoding polyline:", error);
      }
    }
  }, [ambulanceDetails.route]);

  // Initialize Socket.IO connection
  useEffect(() => {
    // Initialize socket connection
    socket.current = io("http://192.168.47.158:5000"); // Replace with your IPv4 WiFi URL
  
    socket.current.on("connect", () => {
      console.log(" Client: Connected to server");
    });
  
    socket.current.on("connect_error", (err) => {
      console.error(" Connection error:", err);
    });
  
    return () => {
      console.log(" Disconnecting socket...");
      socket.current.disconnect();
    };
  }, []); // Runs only once when component mounts
  
  // Event Listener for Route Updates
  useEffect(() => {
    if (!socket.current) return;
  
    const handleRouteUpdate = (data) => {
      console.log("ambulance_route_update EVENT RECEIVED -------------------------------------------------------------");
      console.log(" Route update received:", data);
      setAmbulanceDetails((prevDetails) => ({
        ...prevDetails,
        ...data, // Update route, distance, duration, etc.
      }));
    };
  
    // Attach event listener
    socket.current.on("ambulance_route_update", handleRouteUpdate)
    
  }

  )
  
  //  return () => {
  //    console.log(" Removing event listener for ambulance_route_update...");
  //    socket.current.off("ambulance_route_update", handleRouteUpdate);
  //  };
  //}, []); // Runs once after component mounts
  
  const handleMapLayout = () => {
    setMapLoaded(true);
  };

  const handleSheetChanges = (index) => {
    console.log("BottomSheet position changed to: ", index);
  };

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        onLayout={handleMapLayout}
        region={{
          latitude: ambulanceDetails.latitude,
          longitude: ambulanceDetails.longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        <Marker
          coordinate={{
            latitude: userLocation.latitude,
            longitude: userLocation.longitude,
          }}
          title="Your Location"
        />
        
        <Marker
          coordinate={{
            latitude: ambulanceDetails.latitude,
            longitude: ambulanceDetails.longitude,
          }}
          title="Ambulance Location"
          description={`Ambulance ID: ${ambulanceDetails.ambulance_id}, Type: ${ambulanceDetails.type}`}
        />
      {/*  <Marker
          coordinate={{
            latitude: ambulanceDetails.latitude,
            longitude: ambulanceDetails.longitude,
          }}
          title="Ambulance Location"
          description={`Ambulance ID: ${ambulanceDetails.ambulance_id}, Type: ${ambulanceDetails.type}`}
          
        /> */}
        {decodedPolyline.length > 0 && (
          <Polyline coordinates={decodedPolyline} strokeWidth={5} strokeColor="red" />
        )}
      </MapView>

      {mapLoaded && (
        <BottomSheetComponent
          bottomSheetRef={bottomSheetRef}
          ambulance={ambulanceDetails}
          handleSheetChanges={handleSheetChanges}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: '100%',
    height: '100%',
  },
});

export default AmbTrack;
