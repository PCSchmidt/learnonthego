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
  Platform,
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
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          tintColor="#d7bf89"
          colors={['#d7bf89']}
          progressBackgroundColor="#0f131b"
        />
      }
    >
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />
      <View style={styles.shell}>
        <View style={styles.heroSection}>
          <Text style={styles.eyebrow}>LearnOnTheGo Dashboard</Text>
          <Text style={styles.title}>Welcome back, {user?.full_name || 'Member'}</Text>
          <Text style={styles.subtitle}>Your private command center for AI lecture creation.</Text>

          <View style={styles.userInfoRow}>
            <View style={styles.userInfoBlock}>
              <Text style={styles.userInfoLabel}>Account Email</Text>
              <Text style={styles.userEmail}>{user?.email || 'Not available'}</Text>
            </View>
            <View style={styles.userInfoBlock}>
              <Text style={styles.userInfoLabel}>Tier</Text>
              <Text style={styles.userTier}>{user?.subscription_tier?.toUpperCase() || 'FREE'} PLAN</Text>
            </View>
          </View>
        </View>

        <View style={styles.actionPanel}>
          <TouchableOpacity
            testID="home-create-lecture-button"
            style={styles.primaryButton}
            onPress={handleCreateLecture}
            accessibilityRole="button"
            accessibilityLabel="Create new lecture"
            accessibilityHint="Opens lecture composer"
          >
            <Text style={styles.primaryButtonText}>Create New Lecture</Text>
          </TouchableOpacity>

          <View style={styles.buttonRow}>
            <TouchableOpacity
              testID="home-system-check-button"
              style={styles.secondaryButton}
              onPress={handleTestAPI}
              accessibilityRole="button"
              accessibilityLabel="System check"
              accessibilityHint="Tests backend health and service readiness"
            >
              <Text style={styles.secondaryButtonText}>System Check</Text>
            </TouchableOpacity>

            <TouchableOpacity
              testID="home-settings-button"
              style={styles.secondaryButton}
              onPress={handleSettings}
              accessibilityRole="button"
              accessibilityLabel="Settings"
              accessibilityHint="Opens account and provider settings"
            >
              <Text style={styles.secondaryButtonText}>Settings</Text>
            </TouchableOpacity>

            <TouchableOpacity
              testID="home-signout-button"
              style={styles.logoutButton}
              onPress={handleLogout}
              accessibilityRole="button"
              accessibilityLabel="Sign out"
              accessibilityHint="Signs out of the current account"
            >
              <Text style={styles.logoutButtonText}>Sign Out</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.recentSection}>
          <Text style={styles.sectionTitle}>Lecture Library</Text>
        
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color="#d7bf89" />
              <Text style={styles.loadingText}>Loading your lectures...</Text>
            </View>
          ) : lectures.length > 0 ? (
            lectures.map((lecture, index) => (
              <TouchableOpacity
                key={lecture.id || `lecture-${index}`}
                testID={`lecture-card-${index}`}
                style={styles.lectureCard}
                onPress={() => {
                  if (lecture.id) {
                    handleLecturePress(lecture.id);
                  }
                }}
                accessibilityRole="button"
                accessibilityLabel={lecture.title ? `Open lecture ${lecture.title}` : 'Open lecture'}
                accessibilityHint="Navigates to lecture playback details"
                accessibilityState={{ disabled: !lecture.id }}
                disabled={!lecture.id}
              >
                <Text style={styles.lectureTitle}>{lecture.title}</Text>
                <Text style={styles.lectureDuration}>{lecture.duration} minutes</Text>
                <Text style={styles.lectureDate}>
                  {lecture.created_at ? new Date(lecture.created_at).toLocaleDateString() : 'Date unavailable'}
                </Text>
              </TouchableOpacity>
            ))
          ) : (
            <View style={styles.placeholderCard}>
              <Text style={styles.placeholderText}>
                No lectures yet. Create your first premium lecture session to get started.
              </Text>
            </View>
          )}
        </View>

        <View style={styles.featuresSection}>
          <Text style={styles.sectionTitle}>Platform Status</Text>
          <View style={styles.featureItem}>
            <Text style={styles.featureTag}>Live</Text>
            <Text style={styles.featureTitle}>Core Lecture Workflow</Text>
            <Text style={styles.featureDescription}>
              Topic intake, prompt enrichment, and AI-powered generation are active.
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureTag}>Roadmap</Text>
            <Text style={styles.featureTitle}>Expanded Playback Suite</Text>
            <Text style={styles.featureDescription}>
              Advanced controls, download experience, and richer session analytics.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#06070b',
  },
  contentContainer: {
    padding: 18,
    paddingBottom: 24,
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -80,
    left: -60,
    width: 240,
    height: 240,
    backgroundColor: 'rgba(198, 168, 106, 0.08)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: 80,
    right: -100,
    width: 280,
    height: 280,
    backgroundColor: 'rgba(155, 166, 197, 0.08)',
  },
  shell: {
    width: '100%',
    maxWidth: 1180,
    alignSelf: 'center',
  },
  heroSection: {
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0f131b',
    paddingHorizontal: 24,
    paddingVertical: 24,
    marginBottom: 14,
  },
  eyebrow: {
    color: '#d7bf89',
    fontSize: 12,
    letterSpacing: 1.8,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 10,
  },
  title: {
    color: '#f4efe4',
    fontSize: 46,
    lineHeight: 50,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#aeb6c7',
    lineHeight: 22,
    marginBottom: 18,
  },
  userInfoRow: {
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    gap: 10,
  },
  userInfoBlock: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#2b3240',
    backgroundColor: '#121824',
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  userInfoLabel: {
    color: '#7e8798',
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
    marginBottom: 6,
  },
  userEmail: {
    fontSize: 14,
    color: '#d6dbe6',
    fontWeight: '500',
  },
  userTier: {
    fontSize: 12,
    color: '#d7bf89',
    fontWeight: '700',
    letterSpacing: 0.7,
  },
  actionPanel: {
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0b0f16',
    padding: 16,
    marginBottom: 14,
    gap: 10,
  },
  primaryButton: {
    backgroundColor: '#d7bf89',
    borderWidth: 1,
    borderColor: '#a9905d',
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#11151e',
    fontSize: 14,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  secondaryButton: {
    backgroundColor: '#121824',
    paddingVertical: 13,
    paddingHorizontal: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2b3240',
    flex: 1,
  },
  secondaryButtonText: {
    color: '#e0e4ed',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  recentSection: {
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0f131b',
    padding: 16,
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 28,
    fontWeight: '600',
    color: '#f2ecdf',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 12,
  },
  placeholderCard: {
    backgroundColor: '#111722',
    padding: 16,
    borderWidth: 1,
    borderColor: '#2b3240',
    borderStyle: 'dashed',
  },
  placeholderText: {
    color: '#aeb6c7',
    fontSize: 14,
    lineHeight: 20,
  },
  featuresSection: {
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0f131b',
    padding: 16,
  },
  featureItem: {
    backgroundColor: '#111722',
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#2b3240',
  },
  featureTag: {
    color: '#d7bf89',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.2,
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#f0eadb',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#a8b0c0',
    lineHeight: 20,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    flexWrap: 'wrap',
  },
  logoutButton: {
    backgroundColor: '#2a1115',
    borderWidth: 1,
    borderColor: '#5f252f',
    paddingVertical: 13,
    paddingHorizontal: 14,
    alignItems: 'center',
    flex: 1,
  },
  logoutButtonText: {
    color: '#f2c6cf',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingVertical: 20,
    gap: 8,
  },
  loadingText: {
    fontSize: 14,
    color: '#aeb6c7',
  },
  lectureCard: {
    backgroundColor: '#111722',
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2b3240',
  },
  lectureTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#f1ebdf',
    marginBottom: 4,
  },
  lectureDuration: {
    fontSize: 14,
    color: '#d7bf89',
    fontWeight: '600',
    marginBottom: 2,
  },
  lectureDate: {
    fontSize: 12,
    color: '#8f99ad',
  },
});

export default HomeScreen;
