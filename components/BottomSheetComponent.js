import React, { useState } from 'react';
import { Text, View, StyleSheet, TextInput, Button, Alert } from 'react-native';
import { RadioButton } from 'react-native-paper';
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';

const BottomSheetComponent = ({ bottomSheetRef, ambulance, handleSheetChanges }) => {
  const [name, setName] = useState('');
  const [victims, setVictims] = useState('');
  const [nature, setNature] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [contact, setContact] = useState('');
  const [formVisible, setFormVisible] = useState(true);
  const validatePhoneNumber = (phone) => {
    const regex = /^[0-9]{10}$/;
    return regex.test(phone);
  };

  const handleSubmit = () => {
    if (contact && !validatePhoneNumber(contact)) {
      Alert.alert('Invalid Contact Number', 'Please enter a valid 10-digit phone number.');
      return;
    }

    // Here you can handle the submission (e.g., API call)
    console.log({
      name,
      victims,
      nature,
      age,
      gender,
      contact,
    });
    setFormVisible(false);
    Alert.alert('Submitted', 'Details have been submitted successfully.');
  };

  return (
    <BottomSheet
      ref={bottomSheetRef}
      snapPoints={['15%', '65%','90%']} 
      onChange={handleSheetChanges}
    >
      <BottomSheetView style={styles.contentContainer}>
        <Text variant="titleLarge">Ambulance</Text>
        <Text variant="bodyMedium">Arrive In: {ambulance.time} mins</Text>
        <Text variant="bodyMedium">Distance: {ambulance.dist} km</Text>
        <Text variant="bodyMedium">Speed: {ambulance.speed} m/s</Text>
        <View style={styles.divider} />

        <Text style={styles.header}>Emergency Details</Text>
        {formVisible ? (
            <>
            <TextInput
          style={styles.input}
          placeholder="Name of the person (Optional)"
          value={name}
          onChangeText={setName}
        />
        <TextInput
          style={styles.input}
          placeholder="Approx. number of victims (Optional)"
          value={victims}
          onChangeText={setVictims}
          keyboardType="numeric"
        />

        <TextInput
          style={styles.input}
          placeholder="Nature of the emergency (e.g., trauma, cardiac arrest) (Optional)"
          value={nature}
          onChangeText={setNature}
        />

        <TextInput
          style={styles.input}
          placeholder="Age (Optional)"
          value={age}
          onChangeText={setAge}
          keyboardType="numeric"
        />

        <Text style={styles.label}>Gender (Optional)</Text>
        <RadioButton.Group onValueChange={setGender} value={gender}>
          <View style={styles.radioContainer}>
            <RadioButton value="male" />
            <Text style={styles.radioLabel}>Male</Text>
          
            <RadioButton value="female" />
            <Text style={styles.radioLabel}>Female</Text>
            <RadioButton value="other" />
            <Text style={styles.radioLabel}>Other</Text>
          </View>
        </RadioButton.Group>

        <TextInput
          style={styles.input}
          placeholder="Emergency contact number (Optional)"
          value={contact}
          onChangeText={setContact}
          keyboardType="phone-pad"
        />
        <View style = {styles.buttoncontainer}>
        <Button title="Submit" onPress={handleSubmit} style={styles.button} />
        </View>
            </>
        ) : (<View style={styles.thankYouContainer}>
            <Text style={styles.thankYouText}>
              Thank you! Your information is valuable.
            </Text>
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
      alignItems: 'flex-start',
      justifyContent: 'flex-start',
      backgroundColor: '#ffffff',
    },
    header: {
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 10,
      color: '#333333',
    },
    input: {
      borderWidth: 1,
      borderColor: '#cccccc',
      padding: 10,
      marginBottom: 15,
      borderRadius: 8,
      fontSize: 14, 
      width: '100%',
      backgroundColor: '#f9f9f9',
    },
    label: {
      fontSize: 16,
      marginBottom: 5,
      color: '#555555',
    },
    radioContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 15,
    },
    radioLabel: {
      fontSize: 16,
      color: '#555555',
    },
    checkboxContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 15,
    },
    checkboxLabel: {
      fontSize: 16,
      color: '#555555',
    },
    buttoncontainer: {
        width: '100%',
        flex:1,
      padding: 5,
      alignItems: 'center',
      justifyContent: 'center',
    },
    button:{
        width: '100%',
        padding: 10,
        borderRadius: 8,
    },
    
    divider: {
      alignSelf: 'center',
      marginTop: 30,
      width: '90%',
      height: 1,
      backgroundColor: '#e0e0e0',
      marginVertical: 10,
    },
  });
  
  

export default BottomSheetComponent;
