import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { Appbar } from 'react-native-paper';
import * as Location from 'expo-location';

const SOS = ({ navigation }) => { 
  const [location, setLocation] = useState(null);

  const getLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      alert("Location permission not granted");
      return;
    }
    const currlocation = await Location.getCurrentPositionAsync();
    setLocation(currlocation.coords);
    navigation.navigate('AmbTrack', { location: currlocation.coords }); // Navigate to AmbTrack with location
  };

  return (
    <>
    <View style={styles.img_container}>
      <Image
              source={require('../assets/logo.png')} 
              style={styles.image}
              resizeMode="contain"
            />
    </View>

      <View style={styles.btn_container}>
        <TouchableOpacity onPress={getLocation} style={styles.btn}>
          <Image
            source={require('../assets/SOS_symbol.png')}
            style={styles.sos}
            resizeMode="contain"
          />
        </TouchableOpacity>
        <Text style={styles.title}>SOS Button</Text>
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
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold', // Make the text bold
    marginBottom: 16,
  },
  btn: {
    borderRadius: 50,
    overflow: 'hidden', // Ensures the ripple effect is contained within the image
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
    color: 'rgb(179, 176, 179)', // Light color for the description
  },
  image: {
    width: 200,
    height: 200,
    top:30,
  },
  img_container: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom:100,
  },
});

export default SOS;