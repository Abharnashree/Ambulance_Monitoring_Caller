import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import { io } from 'socket.io-client';
import * as Location from 'expo-location';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SOS = ({ navigation }) => {
  const [location, setLocation] = useState(null);
  const [driverDetails, setDriverDetails] = useState(null); // State to store driver details
  const [phoneNumber, setPhoneNumber] = useState(null);
  const socket = io('http://192.168.47.158:5000', { transports: ['websocket'] });

  // Effect hook to handle socket connection and disconnection
  useEffect(() => {
    socket.connect();

    socket.on("connect", async () => {
      console.log("Socket connected");
    
      try {
        // Retrieve the stored JWT token from AsyncStorage
        const token = await AsyncStorage.getItem("AccessToken");
        
        if (token) {
          // Decode the JWT token to extract the phone number
          const decodedToken = JSON.parse(atob(token.split('.')[1])); 
          const phone = decodedToken.phone_number
          setPhoneNumber(phone); // Extract phone number from token
          console.log("PHONE NUMBER RETRIEVED FROM COOKIE",phone)
          socket.emit('join_room', { room: `caller-${phone}` });
        } else {
          console.error("No token found in storage");
        }
      } catch (error) {
        console.error("Error retrieving phone number:", error);
      }
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
      console.log("Right before navigating",location);
      navigation.navigate('AmbTrack', {
        driverDetails: driverDetails,
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
      const currlocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Highest
      });
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

      const response = await axios.post('http://192.168.47.158:5000/caller/booking', { 
        //use ipconfig and use your own ipv4 address for wifi
        caller_phone_no: phoneNumber, // how to use the o
        latitude: currlocation.coords.latitude,
        longitude: currlocation.coords.longitude,
      });
      console.log("Current location AFTER API response:", currlocation);

      console.log("API Response:", response.data);
      Alert.alert('Success', 'SOS triggered. An ambulance is on its way.');

    } catch (error) {
      console.log("Error:", error.message);
      console.log("Error details:", error);
      Alert.alert('Error', 'An error occurred while triggering the SOS.');
      if (error.response) {
        console.log("Error response data:", error.response.data);
        console.log("Error response status:", error.response.status);
        console.log("Error response headers:", error.response.headers);
        Alert.alert('Error', `Response Error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`);
      } else if (error.request) {
        console.log("Error request:", error.request);
        Alert.alert('Error', 'No response received from the server. Check the server status.');
      } else {
        console.log("Error message:", error.message);
        Alert.alert('Error', `Request failed: ${error.message}`);
      }
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

