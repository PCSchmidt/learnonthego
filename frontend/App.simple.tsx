/**
 * Simple Test App - Minimal React Native Web Test
 */

import React from 'react';
import {View, Text} from 'react-native';

const App: React.FC = () => {
  return (
    <View style={{
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#f8f9fa',
    }}>
      <Text style={{
        fontSize: 24,
        color: '#333',
        fontWeight: 'bold',
      }}>
        LearnOnTheGo Frontend Test
      </Text>
      <Text style={{
        fontSize: 16,
        color: '#666',
        marginTop: 10,
      }}>
        React Native Web is working!
      </Text>
    </View>
  );
};

export default App;
