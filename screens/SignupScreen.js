import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, TextInput, Button } from 'react-native-paper';

const SignupScreen = ({navigation}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign Up</Text> 
      <TextInput label="Name" style={styles.input} />
      <TextInput label="Phone Number" keyboardType="phone-pad" style={styles.input} />
      <TextInput label="Emergency Contact" keyboardType="phone-pad" style={styles.input} />
      <Button mode="contained" 
      style={styles.button}
      onPress={() => navigation.navigate('SOS')}>
        Register
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    marginBottom: 15,
    backgroundColor: '#f5f5f5',
  },
  button: {
    marginTop: 20,
    backgroundColor: '#1E88E5',
  },
});

export default SignupScreen;