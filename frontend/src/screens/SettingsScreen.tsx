/**
 * SettingsScreen - App configuration and user preferences
 * Phase 0: Basic settings placeholder
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';

const SettingsScreen: React.FC = () => {
  const handleAbout = () => {
    Alert.alert(
      'About LearnOnTheGo',
      'Version 1.0.0 - Phase 0\n\nA mobile-first app for converting text topics into personalized audio lectures.\n\nBuilt with React Native, FastAPI, and Railway.'
    );
  };

  const handleTestConnection = async () => {
    try {
      const response = await fetch('https://learnonthego-production.up.railway.app/health');
      const data = await response.json();
      Alert.alert(
        'Connection Test',
        `✅ Connected to backend\n\nStatus: ${data.status}\nMessage: ${data.message}`
      );
    } catch (error) {
      Alert.alert(
        'Connection Test',
        '❌ Failed to connect to backend\n\nPlease check your internet connection.'
      );
    }
  };

  const settingsItems = [
    {
      title: 'Test API Connection',
      description: 'Check backend connectivity',
      onPress: handleTestConnection,
      icon: '🔗',
    },
    {
      title: 'About',
      description: 'App version and information',
      onPress: handleAbout,
      icon: 'ℹ️',
    },
  ];

  const comingSoonItems = [
    {
      title: 'Account Settings',
      description: 'User profile and preferences',
      icon: '👤',
    },
    {
      title: 'Audio Settings',
      description: 'Voice selection and audio quality',
      icon: '🎵',
    },
    {
      title: 'API Keys',
      description: 'Configure OpenRouter and ElevenLabs',
      icon: '🔑',
    },
    {
      title: 'Storage',
      description: 'Manage downloaded lectures',
      icon: '💾',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Available Now</Text>
        {settingsItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={styles.settingItem}
            onPress={item.onPress}>
            <Text style={styles.settingIcon}>{item.icon}</Text>
            <View style={styles.settingContent}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              <Text style={styles.settingDescription}>{item.description}</Text>
            </View>
            <Text style={styles.arrow}>›</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Coming in Phase 1</Text>
        {comingSoonItems.map((item, index) => (
          <View key={index} style={[styles.settingItem, styles.disabledItem]}>
            <Text style={styles.settingIcon}>{item.icon}</Text>
            <View style={styles.settingContent}>
              <Text style={[styles.settingTitle, styles.disabledText]}>
                {item.title}
              </Text>
              <Text style={[styles.settingDescription, styles.disabledText]}>
                {item.description}
              </Text>
            </View>
            <Text style={[styles.arrow, styles.disabledText]}>⏳</Text>
          </View>
        ))}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          LearnOnTheGo v1.0.0 - Phase 0
        </Text>
        <Text style={styles.footerSubtext}>
          Built with ❤️ using cost-conscious architecture
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  section: {
    marginTop: 20,
    marginHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
    marginLeft: 4,
  },
  settingItem: {
    backgroundColor: '#ffffff',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  disabledItem: {
    opacity: 0.6,
  },
  settingIcon: {
    fontSize: 24,
    marginRight: 16,
    width: 32,
    textAlign: 'center',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#6b7280',
  },
  disabledText: {
    color: '#9ca3af',
  },
  arrow: {
    fontSize: 20,
    color: '#6b7280',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    padding: 32,
    marginTop: 20,
  },
  footerText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
  },
});

export default SettingsScreen;
