import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

// URL configuration based on environment
const WEB_APP_URL = __DEV__ 
  ? 'http://localhost:3000'  // Development
  : 'https://appliancerepair.app'; // Production

export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <WebView
          source={{ uri: WEB_APP_URL }}
          style={styles.webview}
          // Enable JavaScript
          javaScriptEnabled={true}
          // Enable DOM storage
          domStorageEnabled={true}
          // Better scrolling experience
          decelerationRate="normal"
          // Handle navigation within WebView
          onNavigationStateChange={(navState) => {
            console.log('Current URL:', navState.url);
          }}
          // Handle loading errors
          onError={(syntheticEvent) => {
            const { nativeEvent } = syntheticEvent;
            console.warn('WebView error:', nativeEvent);
          }}
          // Handle HTTPS requests
          mixedContentMode="compatibility"
          // Enable hardware acceleration
          androidHardwareAccelerationDisabled={false}
          // Hide loading indicator
          startInLoadingState={true}
        />
        <StatusBar style="auto" />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  webview: {
    flex: 1,
  },
});
