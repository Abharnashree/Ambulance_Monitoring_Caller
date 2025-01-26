import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { Marker, Polyline } from 'react-native-maps';
import MapView from 'react-native-maps';
import polyline from '@mapbox/polyline';
import io from 'socket.io-client';
import BottomSheetComponent from '../components/BottomSheetComponent';

const AmbTrack = () => {
  const [ambulanceDetails, setAmbulanceDetails] = useState({
    ambulance_id: 1614,
    distance: '3.0 km',
    duration: '8 mins',
    route: 'grygAwlbfNhES@AFCPBJH@FIPCBA@Cv@Y~JGPHnCLhCJlBVfGHhCL\\?^RrEDpANdENrEX~FTbH@nI?`HGzGEtMEbJsC@uAFgMZmA@Co@',
    type: 'Ambulance_type.BASIC',
    latitude: 11.931972855798419,
    longitude: 79.80786230938979,
  });

  const userLocation = {
    latitude: 11.934842145143234,
    longitude: 79.78588598212839,
  };

  const [decodedPolyline, setDecodedPolyline] = useState([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const bottomSheetRef = useRef(null);
  const socket = useRef(null);

  // Decode polyline whenever the route changes
  useEffect(() => {
    if (ambulanceDetails.route) {
      const decoded = polyline.decode(ambulanceDetails.route).map((coord) => ({
        latitude: coord[0],
        longitude: coord[1],
      }));
      setDecodedPolyline(decoded);
    }
  }, [ambulanceDetails.route]);

  // Initialize Socket.IO connection
  useEffect(() => {
    socket.current = io("http://192.168.161.210:5000"); // Replace with your IPv4 wifi URL
    socket.current.on("connect", () => {
      console.log("Connected to server");
    });

    
    socket.current.on("ambulance_route_update", (data) => {
      console.log("Route update received:", data);
      setAmbulanceDetails((prevDetails) => ({
        ...prevDetails,
        ...data, // Update route, distance, duration, etc.
      }));
    });

    return () => {
      // Clean up the socket connection on component unmount
      socket.current.disconnect();
    };
  }, []);

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
        {decodedPolyline.length > 0 && (
          <Polyline coordinates={decodedPolyline} strokeWidth={3} strokeColor="red" />
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
