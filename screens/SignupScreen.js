import React, { useRef, useState } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { Text, TextInput, Button } from 'react-native-paper';
import { getApp, initializeApp } from 'firebase/app';
import {
  initializeAuth,
  getReactNativePersistence,
  PhoneAuthProvider,
  signInWithCredential,
} from 'firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { FirebaseRecaptchaVerifierModal, FirebaseRecaptchaBanner } from 'expo-firebase-recaptcha';
import fbConfig from '../config/firebase';

// Initialize Firebase
try {
  initializeApp(fbConfig);
} catch (error) {
  console.log('Initializing error:', error);
}

const app = getApp();
const auth = initializeAuth(app, {
  persistence: getReactNativePersistence(AsyncStorage),
});

if (!app?.options || Platform.OS === 'web') {
  throw new Error('This example only works on Android or iOS and requires a valid Firebase config.');
}

const SignupScreen = ({ navigation }) => {
  const recaptchaVerifier = useRef(null);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [verificationId, setVerificationID] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [info, setInfo] = useState('');
  const attemptInvisibleVerification = false;

  const handleSendVerificationCode = async () => {
    try {
      const phoneProvider = new PhoneAuthProvider(auth);
      const verificationId = await phoneProvider.verifyPhoneNumber(phoneNumber, recaptchaVerifier.current);
      setVerificationID(verificationId);
      setInfo('Success: Verification code has been sent to your phone');
    } catch (error) {
      setInfo(`Error: ${error.message}`);
    }
  };

  const handleVerifyVerificationCode = async () => {
    try {
      const credential = PhoneAuthProvider.credential(verificationId, verificationCode);
      await signInWithCredential(auth, credential);
      setInfo('Success: Phone authentication successful');
      navigation.navigate('Welcome');
    } catch (error) {
      setInfo(`Error: ${error.message}`);
    }
  };

  return (
    <View style={styles.container}>
      <FirebaseRecaptchaVerifierModal ref={recaptchaVerifier} firebaseConfig={fbConfig} />
      {info && <Text style={styles.infoText}>{info}</Text>}
      {!verificationId && (
        <View style={styles.inputContainer}>
          <Text style={styles.labelText}>Enter the phone number:</Text>
          <TextInput
            style={styles.input}
            placeholder="+2547000000"
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
      {verificationId && (
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
      {attemptInvisibleVerification && <FirebaseRecaptchaBanner />}
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
