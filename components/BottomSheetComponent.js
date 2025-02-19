import React, { useState } from 'react';
import { Text, View, StyleSheet, TextInput, Button, Alert, TouchableOpacity } from 'react-native';
import { RadioButton } from 'react-native-paper';
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';
import Constants from 'expo-constants';
import { useFonts } from 'expo-font';

const IP = Constants.expoConfig.extra.IP;

const BottomSheetComponent = ({ bottomSheetRef, ambulance, handleSheetChanges }) => {
  const [name, setName] = useState('');
  const [victims, setVictims] = useState('');
  const [nature, setNature] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [contact, setContact] = useState('');
  const [formVisible, setFormVisible] = useState(true);
  
  const [fontsLoaded] = useFonts({
    Poppins: require('../assets/fonts/Poppins-Regular.ttf'),
    PoppinsBold: require('../assets/fonts/Poppins-Bold.ttf'),
  });

  if (!fontsLoaded) return null; 

  const validatePhoneNumber = (phone) => /^[0-9]{10}$/.test(phone);

  const handleSubmit = async () => {
    const patientData = { name, victims, nature, age, gender, contact };
  
    try {
      const response = await fetch(`http://${IP}:5000/submit_patient_details`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patientData),
      });
  
      const result = await response.json();
      Alert.alert("Success", result.message);
      setFormVisible(false);
    } catch (error) {
      console.error("Error submitting details:", error);
      Alert.alert("Error", "Failed to submit details. Please try again.");
    }
  };

  return (
    <BottomSheet ref={bottomSheetRef} snapPoints={['15%', '65%', '90%']} onChange={handleSheetChanges}>
      <BottomSheetView style={styles.contentContainer}>
        <Text style={styles.title}>🚑 Ambulance</Text>
        <Text style={styles.infoText}>🕒 Arrives In: {ambulance.duration}</Text>
        <Text style={styles.infoText}>📍 Distance: {ambulance.distance}</Text>
        <Text style={styles.infoText}>🚗 Ambulance ID: {ambulance.ambulance_id}</Text>
        <View style={styles.divider} />

        <Text style={styles.header}>Emergency Details</Text>
        {formVisible ? (
          <>
            <TextInput style={styles.input} placeholder="Name of the person (Optional)" value={name} onChangeText={setName} />
            <TextInput style={styles.input} placeholder="Approx. number of victims (Optional)" value={victims} onChangeText={setVictims} keyboardType="numeric" />
            <TextInput style={styles.input} placeholder="Nature of the emergency (e.g., trauma, cardiac arrest)" value={nature} onChangeText={setNature} />
            <TextInput style={styles.input} placeholder="Age (Optional)" value={age} onChangeText={setAge} keyboardType="numeric" />

            <Text style={styles.label}>Gender (Optional)</Text>
            <RadioButton.Group onValueChange={setGender} value={gender}>
              <View style={styles.radioContainer}>
                <RadioButton value="male" color="#007BFF" />
                <Text style={styles.radioLabel}>Male</Text>
                <RadioButton value="female" color="#007BFF" />
                <Text style={styles.radioLabel}>Female</Text>
                <RadioButton value="other" color="#007BFF" />
                <Text style={styles.radioLabel}>Other</Text>
              </View>
            </RadioButton.Group>

            <TextInput style={styles.input} placeholder="Emergency contact number (Optional)" value={contact} onChangeText={setContact} keyboardType="phone-pad" />

            <TouchableOpacity style={styles.button} onPress={handleSubmit}>
              <Text style={styles.buttonText}>Submit</Text>
            </TouchableOpacity>
          </>
        ) : (
          <View style={styles.thankYouContainer}>
            <Text style={styles.thankYouText}>🎉 Thank you! Your information is valuable.</Text>
          </View>
        )}
      </BottomSheetView>
    </BottomSheet>
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontFamily: 'PoppinsBold',
    color: '#555',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 16,
    fontFamily: 'Poppins',
    color: '#555',
    marginBottom: 5,
  },
  header: {
    fontSize: 20,
    fontFamily: 'PoppinsBold',
    color: '#555',
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 12,
    borderRadius: 10,
    fontSize: 16,
    fontFamily: 'Poppins',
    backgroundColor: '#f8f9fa',
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    fontFamily: 'Poppins',
    color: '#555',
    marginBottom: 5,
  },
  radioContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  radioLabel: {
    fontSize: 16,
    fontFamily: 'Poppins',
    color: '#555',
    marginRight: 20,
  },
  button: {
    backgroundColor: '#007BFF',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: '#007BFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  buttonText: {
    fontSize: 18,
    fontFamily: 'PoppinsBold',
    color: '#fff',
  },
  divider: {
    alignSelf: 'center',
    width: '90%',
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 15,
  },
  thankYouContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  thankYouText: {
    fontSize: 18,
    fontFamily: 'PoppinsBold',
    color: '#007BFF',
  },
});

export default BottomSheetComponent;
