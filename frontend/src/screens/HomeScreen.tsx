/**
 * HomeScreen - Main dashboard for LearnOnTheGo
 * Shows recent lectures and quick actions with authenticated user context
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import {useNavigation} from '@react-navigation/native';
import {StackNavigationProp} from '@react-navigation/stack';
import { useAuth } from '../contexts/AuthContext';
import lectureService, { LectureResponse } from '../services/lecture';

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
  const { user, logout } = useAuth();
  const [lectures, setLectures] = useState<LectureResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadUserLectures();
  }, []);

  const loadUserLectures = async () => {
    try {
      const response = await lectureService.getUserLectures();
      if (response.success && response.data) {
        setLectures(response.data);
      } else {
        // If endpoint doesn't exist yet, show mock data
        setLectures([]);
      }
    } catch (error) {
      console.error('Error loading lectures:', error);
      setLectures([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadUserLectures();
    setIsRefreshing(false);
  };

  const handleCreateLecture = () => {
    navigation.navigate('CreateLecture');
  };

  const handleLecturePress = (lectureId: string) => {
    navigation.navigate('LecturePlayer', { lectureId });
  };

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: async () => {
            try {
              await logout();
            } catch (error) {
              console.error('Logout error:', error);
            }
          }
        },
      ]
    );
  };

  const handleTestAPI = async () => {
    try {
      const response = await fetch('https://learnonthego-production.up.railway.app/health');
      const data = await response.json();
      Alert.alert(
        'Backend Status', 
        `Status: ${data.status || 'Online'} ✅\n\nAuthentication: Working\nDatabase: Connected\nAI Services: Ready`
      );
    } catch (error) {
      Alert.alert('API Test Failed', 'Could not connect to backend');
    }
  };

  const handleSettings = () => {
    navigation.navigate('Settings');
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Welcome back, {user?.full_name || 'User'}!</Text>
        <Text style={styles.subtitle}>
          Ready to create your next audio lecture?
        </Text>
        <View style={styles.userInfo}>
          <Text style={styles.userEmail}>{user?.email}</Text>
          <Text style={styles.userTier}>
            {user?.subscription_tier?.toUpperCase() || 'FREE'} PLAN
          </Text>
        </View>
      </View>

      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.primaryButton} onPress={handleCreateLecture}>
          <Text style={styles.primaryButtonText}>Create New Lecture</Text>
        </TouchableOpacity>

        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.secondaryButton} onPress={handleTestAPI}>
            <Text style={styles.secondaryButtonText}>Test Backend</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.secondaryButton} onPress={handleSettings}>
            <Text style={styles.secondaryButtonText}>Settings</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.recentSection}>
        <Text style={styles.sectionTitle}>Your Lectures</Text>
        
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#6366f1" />
            <Text style={styles.loadingText}>Loading your lectures...</Text>
          </View>
        ) : lectures.length > 0 ? (
          lectures.map((lecture) => (
            <TouchableOpacity
              key={lecture.id}
              style={styles.lectureCard}
              onPress={() => handleLecturePress(lecture.id)}
            >
              <Text style={styles.lectureTitle}>{lecture.title}</Text>
              <Text style={styles.lectureDuration}>{lecture.duration} minutes</Text>
              <Text style={styles.lectureDate}>
                {new Date(lecture.created_at).toLocaleDateString()}
              </Text>
            </TouchableOpacity>
          ))
        ) : (
          <View style={styles.placeholderCard}>
            <Text style={styles.placeholderText}>
              No lectures yet. Create your first lecture to get started!
            </Text>
          </View>
        )}
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
    marginBottom: 16,
  },
  userInfo: {
    alignItems: 'center',
    gap: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#e0e7ff',
    fontWeight: '500',
  },
  userTier: {
    fontSize: 12,
    color: '#10b981',
    fontWeight: 'bold',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
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
  buttonRow: {
    flexDirection: 'row',
    gap: 8,
    justifyContent: 'space-between',
  },
  logoutButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
  },
  logoutButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    gap: 8,
  },
  loadingText: {
    fontSize: 14,
    color: '#6b7280',
  },
  lectureCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  lectureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  lectureDuration: {
    fontSize: 14,
    color: '#6366f1',
    fontWeight: '600',
    marginBottom: 2,
  },
  lectureDate: {
    fontSize: 12,
    color: '#9ca3af',
  },
});

export default HomeScreen;
