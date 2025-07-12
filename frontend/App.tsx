/**
 * LearnOnTheGo - Main App Component
 * Mobile-first app for converting text topics into personalized audio lectures
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {StatusBar, StyleSheet} from 'react-native';
import {SafeAreaProvider} from 'react-native-safe-area-context';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import CreateLectureScreen from './src/screens/CreateLectureScreen';
import LecturePlayerScreen from './src/screens/LecturePlayerScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Types
export type RootStackParamList = {
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: {lectureId: string};
  Settings: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#6366f1',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}>
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{
              title: 'LearnOnTheGo',
              headerTitleAlign: 'center',
            }}
          />
          <Stack.Screen
            name="CreateLecture"
            component={CreateLectureScreen}
            options={{
              title: 'Create Lecture',
            }}
          />
          <Stack.Screen
            name="LecturePlayer"
            component={LecturePlayerScreen}
            options={{
              title: 'Lecture Player',
            }}
          />
          <Stack.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              title: 'Settings',
            }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
});

export default App;
