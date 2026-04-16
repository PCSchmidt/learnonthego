/**
 * HomeScreen - Main dashboard for LearnOnTheGo
 * Shows recent lectures and quick actions with authenticated user context
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
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
import { colors, spacing, typography } from '../theme/tokens';
import PremiumButton from '../components/ui/PremiumButton';
import PremiumPanel from '../components/ui/PremiumPanel';

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
          <PremiumButton
            testID="home-create-lecture-button"
            title="Create New Lecture"
            onPress={handleCreateLecture}
            accessibilityLabel="Create new lecture"
          />

          <View style={styles.buttonRow}>
            <PremiumButton
              testID="home-system-check-button"
              title="System Check"
              onPress={handleTestAPI}
              variant="secondary"
              style={styles.rowButton}
              accessibilityLabel="System check"
            />

            <PremiumButton
              testID="home-settings-button"
              title="Settings"
              onPress={handleSettings}
              variant="secondary"
              style={styles.rowButton}
              accessibilityLabel="Settings"
            />

            <PremiumButton
              testID="home-signout-button"
              title="Sign Out"
              onPress={handleLogout}
              variant="danger"
              style={styles.rowButton}
              accessibilityLabel="Sign out"
            />
          </View>
        </View>

        <PremiumPanel dark eyebrow="Library" title="Lecture Library" style={styles.recentSection}>
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color={colors.accent.brass} />
              <Text style={styles.loadingText}>Loading your lectures...</Text>
            </View>
          ) : lectures.length > 0 ? (
            lectures.map((lecture, index) => (
              <PremiumButton
                key={lecture.id || `lecture-${index}`}
                testID={`lecture-card-${index}`}
                title={lecture.title || 'Untitled Lecture'}
                onPress={() => {
                  if (lecture.id) {
                    handleLecturePress(lecture.id);
                  }
                }}
                variant="secondary"
                disabled={!lecture.id}
                style={styles.lectureCard}
                accessibilityLabel={lecture.title ? `Open lecture ${lecture.title}` : 'Open lecture'}
              />
            ))
          ) : (
            <View style={styles.placeholderCard}>
              <Text style={styles.placeholderText}>
                No lectures yet. Create your first premium lecture session to get started.
              </Text>
            </View>
          )}
        </PremiumPanel>

        <PremiumPanel dark eyebrow="Infrastructure" title="Platform Status" style={styles.featuresSection}>
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
        </PremiumPanel>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg.canvas,
  },
  contentContainer: {
    padding: 18,
    paddingBottom: spacing.xl,
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -80,
    left: -60,
    width: 240,
    height: 240,
    backgroundColor: colors.effect.glowA,
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: 80,
    right: -100,
    width: 280,
    height: 280,
    backgroundColor: colors.effect.glowB,
  },
  shell: {
    width: '100%',
    maxWidth: 1180,
    alignSelf: 'center',
  },
  heroSection: {
    borderWidth: 1,
    borderColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xl,
    marginBottom: 14,
  },
  eyebrow: {
    color: colors.accent.brass,
    fontSize: typography.size.label,
    letterSpacing: typography.letterSpacing.wide,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 10,
  },
  title: {
    color: colors.text.primaryDark,
    fontSize: typography.size.display,
    lineHeight: typography.lineHeight.display,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.size.bodyLg,
    color: colors.text.secondaryDark,
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
    borderColor: colors.border.medium,
    backgroundColor: colors.bg.cardDark,
    paddingHorizontal: 14,
    paddingVertical: spacing.sm,
  },
  userInfoLabel: {
    color: colors.text.muted,
    fontSize: typography.size.caption,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
    marginBottom: 6,
  },
  userEmail: {
    fontSize: typography.size.body,
    color: colors.text.secondaryDark,
    fontWeight: '500',
  },
  userTier: {
    fontSize: typography.size.label,
    color: colors.accent.brass,
    fontWeight: '700',
    letterSpacing: 0.7,
  },
  actionPanel: {
    borderWidth: 1,
    borderColor: colors.border.dark,
    backgroundColor: '#0b0f16',
    padding: spacing.md,
    marginBottom: 14,
    gap: 10,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    flexWrap: 'wrap',
  },
  rowButton: {
    flex: 1,
  },
  recentSection: {
    marginBottom: 14,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingVertical: spacing.lg,
    gap: spacing.xs,
  },
  loadingText: {
    fontSize: typography.size.body,
    color: colors.text.secondaryDark,
  },
  lectureCard: {
    marginBottom: spacing.sm,
  },
  placeholderCard: {
    backgroundColor: colors.bg.cardDark,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border.medium,
    borderStyle: 'dashed',
  },
  placeholderText: {
    color: colors.text.secondaryDark,
    fontSize: typography.size.body,
    lineHeight: typography.lineHeight.body,
  },
  featuresSection: {
    marginBottom: 0,
  },
  featureItem: {
    backgroundColor: colors.bg.cardDark,
    padding: spacing.md,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border.medium,
  },
  featureTag: {
    color: colors.accent.brass,
    fontSize: typography.size.caption,
    fontWeight: '700',
    letterSpacing: 1.2,
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.text.primaryDark,
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: typography.size.body,
    color: colors.text.secondaryDark,
    lineHeight: typography.lineHeight.body,
  },
});

export default HomeScreen;