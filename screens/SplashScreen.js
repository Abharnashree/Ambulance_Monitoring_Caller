import React, { useEffect } from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SplashScreen = ({ navigation }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      handleGetToken();
    }, 2000);

    return () => clearTimeout(timer); // Cleanup timeout
  }, []);

  const handleGetToken = async () => {
    try {
      const dataToken = await AsyncStorage.getItem("AccessToken");
      console.log("this is from the splash screen ", dataToken);
      navigation.replace(dataToken ? "SOS" : "SignupScreen");
    } catch (error) {
      console.error("Error fetching token:", error);
      navigation.replace("SignupScreen");
    }
  };

  return (
    <View style={styles.container}>
      <Image
        source={require('../assets/logo.png')}
        style={styles.image}
        resizeMode="contain"
      />
      <Text style={styles.title}>Ambulance Monitoring</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  image: {
    width: 350,
    height: 300,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#00008b',
    marginTop: 20,
  },
});

export default SplashScreen;
