
import React, { useEffect, useState, useRef, useContext } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Marker, Polyline } from 'react-native-maps';
import MapView from 'react-native-maps';
import polyline from '@mapbox/polyline';
import BottomSheetComponent from '../components/BottomSheetComponent';

const AmbTrack = ({ route }) => {
  const { driverDetails, userLocation, socket ,phoneNumber} = route.params;
  console.log("Phone Number:", phoneNumber);
  console.log("Driver Details:", driverDetails);
  console.log("User Location:", userLocation);

  const [ambulanceDetails, setAmbulanceDetails] = useState({
    ambulance_id: driverDetails.ambulance_id,
    distance: driverDetails.distance,
    duration: driverDetails.duration,
    route: driverDetails.route,
    type: driverDetails.type,
    latitude: driverDetails.latitude,
    longitude: driverDetails.longitude,
  });

  const [decodedPolyline, setDecodedPolyline] = useState([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const bottomSheetRef = useRef(null);

  useEffect(() => {
    console.log("Updated ambulance details:", ambulanceDetails);
  }, [ambulanceDetails]);

  useEffect(() => {
    if (ambulanceDetails.route) {
      console.log("Decoding new polyline:", ambulanceDetails.route);
      try {
        const decoded = polyline.decode(ambulanceDetails.route).map((coord) => ({
          latitude: coord[0],
          longitude: coord[1],
        }));
        setDecodedPolyline(decoded);
        console.log("Decoded polyline:", decoded);
      } catch (error) {
        console.error("Error decoding polyline:", error);
      }
    }
  }, [ambulanceDetails.route]);

  useEffect(() => {
    if (!socket) return;

    const handleRouteUpdate = (data) => {
      console.log("Route update received:", data);
      setAmbulanceDetails((prevDetails) => ({
        ...prevDetails,
        ...data,
      }));
    };
    // socket.emit('join_room', { room: `caller-${phoneNumber}` });
    socket.on("ambulance_route_update", handleRouteUpdate);

    return () => {
      socket.off("ambulance_route_update", handleRouteUpdate);
    };
  }, [socket]);

  const handleMapLayout = () => {
    setMapLoaded(true);
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
        <Marker coordinate={userLocation} title="Your Location" />
        <Marker
          coordinate={{ latitude: ambulanceDetails.latitude, longitude: ambulanceDetails.longitude }}
          title="Ambulance Location"
          description={`Ambulance ID: ${ambulanceDetails.ambulance_id}, Type: ${ambulanceDetails.type}`}
        />
        {decodedPolyline.length > 0 && (
          <Polyline coordinates={decodedPolyline} strokeWidth={5} strokeColor="red" />
        )}
      </MapView>

      {mapLoaded && (
        <BottomSheetComponent
          bottomSheetRef={bottomSheetRef}
          ambulance={ambulanceDetails}
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