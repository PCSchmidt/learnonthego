import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { View, ActivityIndicator, Text } from 'react-native';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import CreateLectureScreen from './src/screens/CreateLectureScreen';
import LecturePlayerScreen from './src/screens/LecturePlayerScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Types
export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: { lectureId: string };
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

// Loading Component
const LoadingScreen: React.FC = () => (
  <View style={{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  }}>
    <ActivityIndicator size="large" color="#6366f1" />
    <Text style={{
      marginTop: 16,
      fontSize: 16,
      color: '#6b7280',
    }}>
      Loading LearnOnTheGo...
    </Text>
  </View>
);

// Authentication Router
const AuthRouter: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#6366f1',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {user ? (
          // Authenticated user screens
          <>
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
          </>
        ) : (
          // Guest user screens
          <>
            <Stack.Screen 
              name="Login" 
              component={LoginScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen 
              name="Register" 
              component={RegisterScreen}
              options={{ headerShown: false }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <AuthProvider>
      <AuthRouter />
    </AuthProvider>
  );
};

export default App;


