import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, Pressable, StatusBar, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
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

const HeaderButton: React.FC<{ icon: string; onPress: () => void; label: string }> = ({ icon, onPress, label }) => (
  <Pressable onPress={onPress} accessibilityRole="button" accessibilityLabel={label} hitSlop={6} style={{ paddingHorizontal: 10 }}>
    <Ionicons name={icon as any} size={22} color="#F8FAFC" />
  </Pressable>
);

const AppNavigator: React.FC = () => {
  const { isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  const handleLogout = () => { logout(); };

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
            <Stack.Screen
              name="Home"
              component={HomeScreen}
              options={({ navigation }) => ({
                title: 'LearnOnTheGo',
                headerRight: () => (
                  <View style={{ flexDirection: 'row', alignItems: 'center', marginRight: 6 }}>
                    <HeaderButton icon="settings-outline" onPress={() => navigation.navigate('Settings')} label="Settings" />
                    <HeaderButton icon="log-out-outline" onPress={handleLogout} label="Log out" />
                  </View>
                ),
              })}
            />
            <Stack.Screen
              name="CreateLecture"
              component={CreateLectureScreen}
              options={({ navigation }) => ({
                title: 'Create Lecture',
                headerRight: () => (
                  <View style={{ flexDirection: 'row', alignItems: 'center', marginRight: 6 }}>
                    <HeaderButton icon="home-outline" onPress={() => navigation.navigate('Home')} label="Home" />
                    <HeaderButton icon="log-out-outline" onPress={handleLogout} label="Log out" />
                  </View>
                ),
              })}
            />
            <Stack.Screen
              name="LecturePlayer"
              component={LecturePlayerScreen}
              options={({ navigation }) => ({
                title: 'Lecture Player',
                headerRight: () => (
                  <View style={{ flexDirection: 'row', alignItems: 'center', marginRight: 6 }}>
                    <HeaderButton icon="home-outline" onPress={() => navigation.navigate('Home')} label="Home" />
                    <HeaderButton icon="log-out-outline" onPress={handleLogout} label="Log out" />
                  </View>
                ),
              })}
            />
            <Stack.Screen
              name="Settings"
              component={SettingsScreen}
              options={({ navigation }) => ({
                title: 'Settings',
                headerRight: () => (
                  <View style={{ flexDirection: 'row', alignItems: 'center', marginRight: 6 }}>
                    <HeaderButton icon="home-outline" onPress={() => navigation.navigate('Home')} label="Home" />
                    <HeaderButton icon="log-out-outline" onPress={handleLogout} label="Log out" />
                  </View>
                ),
              })}
            />
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
