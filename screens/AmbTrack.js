import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Text } from 'react-native-paper';
import MapView, { Marker, UrlTile, Polyline } from 'react-native-maps';
import { StyleSheet, View, ActivityIndicator } from 'react-native';
import axios from 'axios';
import BottomSheetComponent from '../components/BottomSheetComponent';
const AmbTrack = ({ route }) => {
  const { location } = route.params;
  const [ambulance, setAmbulance] = useState({
    latitude: 13.020078,
    longitude: 80.224613,
    time: 5,
    dist: 1.5,
    speed: 10,
  });
  const [routeCoordinates, setRouteCoordinates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const bottomSheetRef = useRef(null);

  const fetchRoute = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('https://api.openrouteservice.org/v2/directions/driving-car', {
        params: {
          api_key: '5b3ce3597851110001cf62483361e889f60c484292407670b3cadcb2',
          start: `${location.longitude},${location.latitude}`,
          end: `${ambulance.longitude},${ambulance.latitude}`,
        },
      });
      const coordinates = response.data.features[0].geometry.coordinates.map(coord => ({
        latitude: coord[1],
        longitude: coord[0],
      }));
      setRouteCoordinates(coordinates);
    } catch (error) {
      console.error('Error fetching route:', error);
    } finally {
      setIsLoading(false);
    }
  }, [location, ambulance]);

  useEffect(() => {
    fetchRoute();
  }, [fetchRoute]);

  const handleSheetChanges = useCallback((index) => {
    console.log('handleSheetChanges', index);
  }, []);

  return (
    <View style={styles.container}>
      {isLoading && (
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#0000ff" />
        </View>
      )}
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: location.latitude,
          longitude: location.longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        <UrlTile
          urlTemplate="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          zIndex={0}
        />
        <Marker coordinate={{ latitude: location.latitude, longitude: location.longitude }} />
        <Marker coordinate={{ latitude: ambulance.latitude, longitude: ambulance.longitude }} />
        {routeCoordinates.length > 0 && (
          <Polyline
            coordinates={routeCoordinates}
            strokeWidth={3}
            strokeColor="black"
          />
        )}
      </MapView>
      <BottomSheetComponent 
        bottomSheetRef={bottomSheetRef} 
        ambulance={ambulance} 
        handleSheetChanges={handleSheetChanges} 
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: '100%',
    height: '85%',
  },
  loader: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -20 }, { translateY: -20 }],
    zIndex: 10,
  },
});

export default AmbTrack;
