import React, { useEffect, useState } from 'react';
import { Card, Text } from 'react-native-paper';
import MapView, { Marker, UrlTile, Polyline } from 'react-native-maps';
import { StyleSheet, View } from 'react-native';
import axios from 'axios';

const AmbTrack = ({ route }) => {
  const { location } = route.params;
  const ambulance = { latitude: 13.020078, longitude: 80.224613, time: 5, dist: 1.5, speed: 10 };
  const [routeCoordinates, setRouteCoordinates] = useState([]);

  useEffect(() => {
    const fetchRoute = async () => {
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
      }
    };

    fetchRoute();
  }, [location, ambulance]);

  return (
    <View style={styles.container}>
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
        <Marker
          key="ambulance-marker"
          coordinate={{ latitude: ambulance.latitude, longitude: ambulance.longitude }}
        />
        <Marker
          key="location-marker"
          coordinate={{ latitude: location.latitude, longitude: location.longitude }}
        />
        {routeCoordinates.length > 0 && (
          <Polyline
            coordinates={routeCoordinates}
            strokeWidth={3}
            strokeColor="black"
          />
        )}
      </MapView>
      <Card style={styles.details}>
        <Card.Content>
          <Text variant="titleLarge">Ambulance</Text>
          <Text variant="bodyMedium">Arrive In: {ambulance.time} mins</Text>
          <Text variant="bodyMedium">Distance: {ambulance.dist} km</Text>
          <Text variant="bodyMedium">Speed: {ambulance.speed} m/s</Text>
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  map: {
    flex: 1,
  },
  details: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    elevation: 5, // Adds shadow for Android
    shadowColor: '#000', // Adds shadow for iOS
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    padding: 15,
  },
});

export default AmbTrack;
