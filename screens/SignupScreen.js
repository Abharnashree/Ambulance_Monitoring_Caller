import React, { useRef, useState } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { Text, TextInput, Button } from 'react-native-paper';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const SignupScreen = ({ navigation }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [info, setInfo] = useState('');
  const[sent, setSent] = useState(false);
  const[verificationCode, setVerificationCode] = useState('');
  const[name, setName]=useState('');

  const handleSendVerificationCode = async () => {
    try {
      const response = await axios.post('http://192.168.113.158:5000/sendOtp',{
        phoneNumber,
      });
      if (response.data.status === 'OTP sent') {
        setInfo('Success: Verification code has been sent to your phone');
        setSent(true); 
      } else {
        setInfo('Error: Failed to send OTP');
      }
    } catch (error) {
      console.error(error);
      setInfo(`Error: ${error.response?.data?.error || error.message}`);
    }
  };

  const handleVerifyVerificationCode = async () => {
    try {
      // Ensure token is available in the response
      const response = await axios.post('http://192.168.113.158:5000/verifyOtp', {
        verificationCode,
        phoneNumber,
        name,
      });

      if (response.data.status === 'success') {
        setInfo('Signed in successfully');
        // Assuming the response contains a JWT token
        const { token } = response.data; // Get token from response

        // Store the JWT token securely
        try {
          await SecureStore.setItemAsync('authToken', token);
          console.log('Token stored successfully');
        } catch (error) {
          console.error('Error storing the token', error);
        }

        navigation.navigate('SOS'); // Navigate to the SOS screen after success
      } else {
        setInfo('Error: Verification failed');
      }
    } catch (error) {
      console.error(error);
      setInfo(`Error: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <View style={styles.container}>
      {info && <Text style={styles.infoText}>{info}</Text>}
      {!sent && (
        <View style={styles.inputContainer}>
          <Text style={styles.labelText}>Enter name: </Text>
          <TextInput
            style={styles.input}
            placeholder="Enter name"
            onChangeText={setName}
          />

          <Text style={styles.labelText}>Enter the phone number:</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter number"
            onChangeText={setPhoneNumber}
          />

          <Button
            style={styles.button}
            mode="contained"
            onPress={handleSendVerificationCode}
            disabled={!phoneNumber.trim()}
          >
            Send Verification Code
          </Button>
        </View>
      )}
      {sent && (
        <View style={styles.inputContainer}>
          <Text style={styles.labelText}>Enter the verification code:</Text>
          <TextInput
            style={styles.input}
            placeholder="123456"
            mode="outlined"
            keyboardType="number-pad"
            onChangeText={setVerificationCode}
          />
          <Button
            style={styles.button}
            mode="contained"
            onPress={handleVerifyVerificationCode}
            disabled={!verificationCode.trim()}
          >
            Confirm Verification Code
          </Button>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'center',
    padding: 20,
  },
  inputContainer: {
    marginBottom: 20,
  },
  labelText: {
    fontSize: 16,
    marginBottom: 10,
    color: '#333',
  },
  input: {
    marginBottom: 20,
  },
  button: {
    marginTop: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#ff0000',
    textAlign: 'center',
    marginBottom: 20,
  },
});

export default SignupScreen;
