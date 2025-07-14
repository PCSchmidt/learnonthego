/**
 * LearnOnTheGo - Authenticated App Entry Point
 * Integrates React Native frontend with FastAPI authentication backend
 * Track B: Authentication Integration Phase 2e
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { StatusBar, View, Text, ActivityIndicator, StyleSheet } from 'react-native';

// Authentication Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';

// Main App Screens
import HomeScreen from './src/screens/HomeScreen';
import CreateLectureScreen from './src/screens/CreateLectureScreen';
import LecturePlayerScreen from './src/screens/LecturePlayerScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createStackNavigator();

// Loading Component
const LoadingScreen: React.FC = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#007AFF" />
    <Text style={styles.loadingText}>Loading...</Text>
  </View>
);

// Authentication Stack (Login/Register)
const AuthStack: React.FC = () => (
  <Stack.Navigator 
    initialRouteName="Login"
    screenOptions={{
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#FFFFFF',
      headerTitleStyle: { fontWeight: 'bold' },
    }}
  >
    <Stack.Screen 
      name="Login" 
      component={LoginScreen} 
      options={{ title: 'Sign In' }}
    />
    <Stack.Screen 
      name="Register" 
      component={RegisterScreen} 
      options={{ title: 'Create Account' }}
    />
  </Stack.Navigator>
);

// Main App Stack (Authenticated User)
const AppStack: React.FC = () => (
  <Stack.Navigator 
    initialRouteName="Home"
    screenOptions={{
      headerStyle: { backgroundColor: '#007AFF' },
      headerTintColor: '#FFFFFF',
      headerTitleStyle: { fontWeight: 'bold' },
    }}
  >
    <Stack.Screen 
      name="Home" 
      component={HomeScreen} 
      options={{ title: 'LearnOnTheGo' }}
    />
    <Stack.Screen 
      name="CreateLecture" 
      component={CreateLectureScreen} 
      options={{ title: 'Create Lecture' }}
    />
    <Stack.Screen 
      name="LecturePlayer" 
      component={LecturePlayerScreen} 
      options={{ title: 'Playing Lecture' }}
    />
    <Stack.Screen 
      name="Settings" 
      component={SettingsScreen} 
      options={{ title: 'Settings' }}
    />
  </Stack.Navigator>
);

// App Navigation Controller
const AppNavigator: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

// Main App Component with Authentication Provider
const App: React.FC = () => {
  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#007AFF" />
      <AuthProvider>
        <AppNavigator />
      </AuthProvider>
    </>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666666',
  },
});

export default App;
