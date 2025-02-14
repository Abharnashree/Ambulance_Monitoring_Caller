
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
    },
    "extra":{
      IP: process.env.IP,  
    }
  },
}
