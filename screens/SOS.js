import React, { useState } from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { Button } from 'react-native-paper';
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
    <View style={styles.btn_container}>
        <Image
                source={require('../assets/logo.jpg')} 
                style={styles.image}
                resizeMode="contain"
              />
      <Text style={styles.title}>BOOK NOW</Text>
      <Button mode="contained" onPress={getLocation} style={styles.btn}>
        SOS
      </Button>
    </View>
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
    marginBottom: 16,
  },
  btn: {
    marginTop: 20,
    backgroundColor: '#00008b',
    borderRadius: 25,
    paddingHorizontal: 30,
    paddingVertical: 8,
  },
  image: {
    width: 150,
    height: 150,
    marginBottom: 20,
  },
});

export default SOS;