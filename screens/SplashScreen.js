import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Image, Animated, Easing} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SplashScreen = ({ navigation }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      handleGetToken();
    }, 4000);

    return () => clearTimeout(timer); // Cleanup timeout
  }, 
  []);

  const handleGetToken = async () => {
    try {
      const dataToken = await AsyncStorage.getItem("AccessToken");
      console.log("this is from the splash screen ", dataToken);
      navigation.replace(dataToken ? "SOS" : "Signup");
    } catch (error) {
      console.error("Error fetching token:", error);
      navigation.replace("Signup");
    }
  };

  const fadeAnim = useRef(new Animated.Value(0)).current; 
  const ambulanceAnim = useRef(new Animated.Value(-500)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current; 

  useEffect(() => {
    Animated.sequence([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000, 
        easing: Easing.ease, 
        useNativeDriver: true,
      }),
      Animated.timing(ambulanceAnim, {
        toValue: 0,
        duration: 1500, 
        easing: Easing.out(Easing.quad), 
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, ambulanceAnim]);

  return (
    <View style={styles.container}>
      <Animated.Image
        source={require('../assets/Ambulance.png')}
        style={[
          styles.ambulance,
          {
            opacity: fadeAnim,
            transform: [
              { translateX: ambulanceAnim },
              { scale: scaleAnim },
            ],
          },
        ]}
        resizeMode="contain"
      />
     
      <Image
        source={require('../assets/Blank logo.png')} 
        style={styles.logo}
        resizeMode="contain"
      />
      <Animated.Text style={[styles.title, { opacity: fadeAnim }]}>
        ResQLink
      </Animated.Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f8f8f8', 
  },
  ambulance: {
    width: 350,  
    height: 250,
    marginBottom: 0, 
  },
  logo: {
    width: 250,
    height: 250,
    marginTop: -250,
  },
  title: {
    fontSize: 36,
    fontWeight: '700', 
    color: '#2a2a72', 
    letterSpacing: 2, 
    marginTop: 20,
  },
});

export default SplashScreen;