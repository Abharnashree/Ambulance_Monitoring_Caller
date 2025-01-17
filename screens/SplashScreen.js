import React, { useEffect } from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text, Button } from 'react-native-paper';

const SplashScreen = ({ navigation }) => {
 

  return (
    <View style={styles.container}>
        <Image
        source={require('../assets/logo.png')} 
        style={styles.image}
        resizeMode="contain"
      />
      <Text style={styles.title}>Ambulance Monitoring</Text>
      <Button
        mode="contained"
        onPress={() => navigation.navigate('Signup')}
        style={styles.button}
        labelStyle={styles.buttonLabel}
      >
        Sign Up
      </Button>
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
  button: {
    marginTop: 20,
    backgroundColor: '#00008b',
    borderRadius: 25,
    paddingHorizontal: 30,
    paddingVertical: 8,
  },
  buttonLabel: {
    fontSize: 16,
    color: '#ffffff',
  },
});

export default SplashScreen;
