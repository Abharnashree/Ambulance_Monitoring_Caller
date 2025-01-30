import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

import SplashScreen from "../screens/SplashScreen"; 
import SignupScreen from "../screens/SignupScreen"; 
import SOS from "../screens/SOS";
import AmbTrack from "../screens/AmbTrack";

const Stack = createNativeStackNavigator();

const checkIfLoggedIn = async () => {
  const token = await SecureStore.getItemAsync('authToken');
  return token ? true : false;
};

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkLoginStatus = async () => {
      const loggedIn = await checkIfLoggedIn();
      setIsLoggedIn(loggedIn);
    };

    checkLoginStatus();
  }, []);

    return (
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {isLoggedIn ? (
            <Stack.Screen name="SOS" component={SOS} />
          ) : (
            <Stack.Screen name="Splash" component={SplashScreen} />
          )}
          <Stack.Screen name="Signup" component={SignupScreen} />
          <Stack.Screen name="SOS" component={SOS}/> 
          <Stack.Screen name="AmbTrack" component={AmbTrack}/> 
        </Stack.Navigator>
      </NavigationContainer>
    );
};

export default App;
