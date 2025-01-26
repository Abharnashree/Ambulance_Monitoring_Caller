
export default{
  "expo": {
    "name": "Ambulance_Monitoring",
    "slug": "Ambulance_Monitoring",
    "plugins":["@react-native-firebase/app","@react-native-firebase/auth"],
    "scheme": "ambi",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "newArchEnabled": true,
    "splash": {
      "image": "./assets/splash-icon.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "config": {
        "googleMaps": {
          "apiKey": "AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0"
        }
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION"
      ],
      "config": {
        "googleMaps": {
          "apiKey": "AIzaSyDJfABDdpB7fIMs_F4e1IeqKoEQ2BSNSl0"
        }
      }
    },
    "config":  {
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  },
  "extra" :{
    firebaseApiKey: "AIzaSyAMpO3wpPjo0U8zUqvY9aNIKYJfKK82vRg",
    firebaseAuthDomain: "ambulancemonitoring-8390b.firebaseapp.com",
    firebaseProjectId: "ambulancemonitoring-8390b",
    firebaseStorageBucket: "ambulancemonitoring-8390b.appspot.com",
    firebaseMessagingSenderId: "576771360683",
    firebaseAppId: "1:576771360683:web:a349f499c4c9ab236634ee"
  }
}
