/**
 * HomeScreen - Main dashboard for LearnOnTheGo
 * Shows recent lectures and quick actions
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
import {useNavigation} from '@react-navigation/native';
import {StackNavigationProp} from '@react-navigation/stack';
// Types
type RootStackParamList = {
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: {lectureId: string};
  Settings: undefined;
};

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();

  const handleCreateLecture = () => {
    navigation.navigate('CreateLecture');
  };

  const handleTestAPI = async () => {
    try {
      const response = await fetch('https://learnonthego-production.up.railway.app/status');
      const data = await response.json();
      Alert.alert(
        'Development Status', 
        `Phase: ${data.phase}\n\nNext: ${data.next_features.slice(0, 2).join('\n')}\n\nBackend: Online ✅\nFrontend: Online ✅`
      );
    } catch (error) {
      Alert.alert('API Test Failed', 'Could not connect to backend');
    }
  };

  const handleSettings = () => {
    navigation.navigate('Settings');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Welcome to LearnOnTheGo</Text>
        <Text style={styles.subtitle}>
          Convert topics into personalized audio lectures
        </Text>
        <Text style={styles.version}>
          Phase 1 MVP - Last updated: {new Date().toLocaleString()}
        </Text>
        <Text style={styles.phaseStatus}>
          🚀 Backend & Frontend Deployed | Next: AI Integration
        </Text>
      </View>

      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.primaryButton} onPress={handleCreateLecture}>
          <Text style={styles.primaryButtonText}>Create New Lecture</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={handleTestAPI}>
          <Text style={styles.secondaryButtonText}>Test API Connection</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondaryButton} onPress={handleSettings}>
          <Text style={styles.secondaryButtonText}>Settings</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.recentSection}>
        <Text style={styles.sectionTitle}>Recent Lectures</Text>
        <View style={styles.placeholderCard}>
          <Text style={styles.placeholderText}>
            No lectures yet. Create your first lecture to get started!
          </Text>
        </View>
      </View>

      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>Phase 0 Features</Text>
        <View style={styles.featureItem}>
          <Text style={styles.featureTitle}>✅ Basic Text-to-Lecture</Text>
          <Text style={styles.featureDescription}>
            Enter any topic and generate a mock lecture
          </Text>
        </View>
        <View style={styles.featureItem}>
          <Text style={styles.featureTitle}>🔄 Coming in Phase 1</Text>
          <Text style={styles.featureDescription}>
            PDF processing, real TTS, user authentication
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 24,
    backgroundColor: '#6366f1',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#e0e7ff',
    textAlign: 'center',
    lineHeight: 22,
  },
  version: {
    fontSize: 14,
    color: '#e0e7ff',
    textAlign: 'center',
    marginTop: 4,
  },
  phaseStatus: {
    fontSize: 12,
    color: '#10b981',
    textAlign: 'center',
    marginTop: 2,
    fontWeight: '500',
  },
  actionButtons: {
    padding: 20,
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#6366f1',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#ffffff',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  secondaryButtonText: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: '600',
  },
  recentSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  placeholderCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderStyle: 'dashed',
    alignItems: 'center',
  },
  placeholderText: {
    color: '#6b7280',
    fontSize: 16,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  featuresSection: {
    padding: 20,
    paddingTop: 0,
  },
  featureItem: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
});

export default HomeScreen;
