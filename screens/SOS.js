import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import { io } from 'socket.io-client';
import * as Location from 'expo-location';
import axios from 'axios';

const SOS = ({ navigation }) => {
  const [location, setLocation] = useState(null);
  const [driverDetails, setDriverDetails] = useState(null); // State to store driver details
  const socket = io('http://192.168.161.210:5000', { transports: ['websocket'] });

  // Effect hook to handle socket connection and disconnection
  useEffect(() => {
    socket.connect();

    socket.on("connect", () => {
      console.log("Socket connected");
      socket.emit('join_room', { room: 'caller-7418581672' });
    });

    socket.on("driver_details", (data) => {
      console.log('Driver details received:', data);
      setDriverDetails(data); // Save driver details when received
    });

    return () => {
      socket.disconnect(); // Cleanup socket connection on unmount
    };
  }, []);

  // Effect hook to navigate once driver details are available
  useEffect(() => {
    if (driverDetails && location) {
      console.log("Driver details and location available, navigating...");
      navigation.navigate('AmbTrack', {
        driverDetails,
        userLocation: location,
      });
    }
  }, [driverDetails, location, navigation]);

  const getLocationAndTriggerSOS = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        alert("Location permission not granted");
        return;
      }
      const currlocation = await Location.getCurrentPositionAsync();
      console.log("The currlocation : ----------------------------");
      console.log(currlocation);

      if (!currlocation.coords || !currlocation.coords.latitude || !currlocation.coords.longitude) {
        Alert.alert('Error', 'Unable to fetch location coordinates.');
        return;
      }

      console.log("The location :---------------------------------");
      console.log(currlocation.coords);

      setLocation(currlocation.coords);
      console.log("Current location BEFORE API response:", currlocation);

      const response = await axios.post('http://192.168.161.210:5000/caller/booking', {
        caller_phone_no: '7418581672', // Replace with the actual phone number
        latitude: currlocation.coords.latitude,
        longitude: currlocation.coords.longitude,
      });
      console.log("Current location AFTER API response:", currlocation);

      console.log("API Response:", response.data);
      Alert.alert('Success', 'SOS triggered. An ambulance is on its way.');

    } catch (error) {
      console.log("Error:", error.message);
      Alert.alert('Error', 'An error occurred while triggering the SOS.');
    }
  };

  return (
    <>
      

      <View style={styles.btn_container}>
        <TouchableOpacity onPress={getLocationAndTriggerSOS} style={styles.btn}>
          <Image
            source={require('../assets/SOS_symbol.png')}
            style={styles.sos}
            resizeMode="contain"
          />
        </TouchableOpacity>
        <Text style={styles.description}>
          Press the SOS button to send an immediate distress signal. An ambulance will be dispatched to your location to provide assistance as quickly as possible.
        </Text>
      </View>
    </>
  );
};

const styles = StyleSheet.create({
  btn_container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  btn: {
    borderRadius: 50,
    overflow: 'hidden',
    alignItems: 'center',
  },
  sos: {
    width: 300,
    height: 300,
  },
  description: {
    marginTop: 20,
    fontSize: 16,
    textAlign: 'center',
    paddingHorizontal: 20,
    color: 'rgb(179, 176, 179)',
  },
  image: {
    width: 200,
    height: 200,
    top: 30,
  },
  img_container: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 100,
  },
});

export default SOS;

