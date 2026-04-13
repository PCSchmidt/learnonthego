import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, StatusBar, Text, View } from 'react-native';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';

import CreateLectureScreen from './src/screens/CreateLectureScreen';
import HomeScreen from './src/screens/HomeScreen';
import LecturePlayerScreen from './src/screens/LecturePlayerScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import SettingsScreen from './src/screens/SettingsScreen';

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: { lectureId: string };
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

const LoadingScreen: React.FC = () => (
  <View
    style={{
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#0B1020',
    }}
  >
    <ActivityIndicator size="large" color="#22D3EE" />
    <Text
      style={{
        marginTop: 14,
        color: '#CBD5E1',
        fontSize: 15,
      }}
    >
      Loading workspace
    </Text>
  </View>
);

const AppNavigator: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#111827' },
          headerTintColor: '#F8FAFC',
          headerTitleStyle: { fontWeight: '600' },
          cardStyle: { backgroundColor: '#F1F5F9' },
        }}
      >
        {isAuthenticated ? (
          <>
            <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'LearnOnTheGo' }} />
            <Stack.Screen name="CreateLecture" component={CreateLectureScreen} options={{ title: 'Create Lecture' }} />
            <Stack.Screen name="LecturePlayer" component={LecturePlayerScreen} options={{ title: 'Lecture Player' }} />
            <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Settings' }} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: false }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const App: React.FC = () => (
  <>
    <StatusBar barStyle="light-content" backgroundColor="#111827" />
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  </>
);

export default App;
