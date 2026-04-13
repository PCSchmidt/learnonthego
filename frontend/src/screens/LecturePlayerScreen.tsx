/**
 * LecturePlayerScreen - Audio player for lectures
 * Phase 0: Placeholder for future audio playback functionality
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from 'react-native';
import {useNavigation, useRoute} from '@react-navigation/native';

const LecturePlayerScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const lectureId = (route.params as any)?.lectureId || 'unknown';

  return (
    <View style={styles.container}>
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />
      <View style={styles.playerCard}>
        <View style={styles.headerRail}>
          <Text style={styles.eyebrow}>Playback Suite</Text>
          <Text style={styles.title}>Lecture Player</Text>
          <Text style={styles.subtitle}>Lecture ID: {lectureId}</Text>
        </View>

        <View style={styles.contentPanel}>
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>Audio Engine Expansion in Progress</Text>
            <Text style={styles.description}>
              Phase 1 will introduce precise controls for play/pause, timeline seeking, variable speed,
              and offline access.
            </Text>
          </View>

          <View style={styles.featureRow}>
            <View style={styles.featureCard}>
              <Text style={styles.featureLabel}>Control</Text>
              <Text style={styles.featureValue}>Timeline + Speed</Text>
            </View>
            <View style={styles.featureCard}>
              <Text style={styles.featureLabel}>Availability</Text>
              <Text style={styles.featureValue}>Offline Downloads</Text>
            </View>
            <View style={styles.featureCard}>
              <Text style={styles.featureLabel}>Quality</Text>
              <Text style={styles.featureValue}>Premium Audio Fidelity</Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}>
            <Text style={styles.backButtonText}>Back to Home</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#06070b',
    padding: 18,
    justifyContent: 'center',
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -80,
    left: -70,
    width: 250,
    height: 250,
    backgroundColor: 'rgba(198, 168, 106, 0.08)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -80,
    right: -100,
    width: 280,
    height: 280,
    backgroundColor: 'rgba(155, 166, 197, 0.08)',
  },
  playerCard: {
    width: '100%',
    maxWidth: 1080,
    alignSelf: 'center',
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0b0d12',
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
  },
  headerRail: {
    flex: 0.9,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
    borderBottomWidth: Platform.OS === 'web' ? 0 : 1,
    borderRightColor: '#242a37',
    borderBottomColor: '#242a37',
    backgroundColor: '#0f131b',
    paddingHorizontal: 24,
    paddingVertical: 24,
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
    fontSize: 44,
    lineHeight: 48,
    fontWeight: '600',
    color: '#f4efe4',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#aeb6c7',
  },
  contentPanel: {
    flex: 1.1,
    backgroundColor: '#f2f0ea',
    padding: 20,
  },
  placeholder: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    padding: 16,
    marginBottom: 14,
  },
  placeholderText: {
    fontSize: 13,
    color: '#2b3240',
    marginBottom: 10,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  description: {
    fontSize: 14,
    color: '#616979',
    lineHeight: 20,
  },
  featureRow: {
    gap: 10,
    marginBottom: 14,
  },
  featureCard: {
    backgroundColor: '#111722',
    borderWidth: 1,
    borderColor: '#2b3240',
    padding: 12,
  },
  featureLabel: {
    color: '#7e8798',
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 6,
  },
  featureValue: {
    color: '#f0eadb',
    fontSize: 14,
    fontWeight: '600',
  },
  backButton: {
    backgroundColor: '#d7bf89',
    borderWidth: 1,
    borderColor: '#a9905d',
    paddingVertical: 13,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  backButtonText: {
    color: '#11151e',
    fontSize: 13,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
});

export default LecturePlayerScreen;
