import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import SplashScreen from "../screens/SplashScreen"; 
import SignupScreen from "../screens/SignupScreen"; 

const Stack = createNativeStackNavigator();

const linking = {
    prefixes: ["ambi://", "exp://"],
    config: {
        screens: {
            Splash: '/',
            SignUp: '/signup',
        },
    },
};

const App = () => {
    return (
      <NavigationContainer linking={linking}>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Splash" component={SplashScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    );
};

export default App;
