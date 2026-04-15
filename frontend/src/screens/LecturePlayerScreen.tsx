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
  const citations = (route.params as any)?.citations || [];
  const sourceContext = (route.params as any)?.sourceContext || null;

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

          {sourceContext || (Array.isArray(citations) && citations.length > 0) ? (
            <View
              style={styles.placeholder}
              accessible
              accessibilityLabel="Source context"
              accessibilityHint="Shows source URI and citation references used for this lecture"
            >
              <Text style={styles.placeholderText}>Source Context</Text>
              {sourceContext?.source_uri ? (
                <Text style={styles.description}>Primary URI: {sourceContext.source_uri}</Text>
              ) : null}
              {sourceContext?.retrieval_method ? (
                <Text style={styles.description}>Retrieval: {sourceContext.retrieval_method}</Text>
              ) : null}
              {sourceContext?.source_class ? (
                <Text style={styles.description}>Class: {sourceContext.source_class}</Text>
              ) : null}
              {Array.isArray(citations)
                ? citations.map((citation: any, index: number) => (
                    <Text key={`${citation?.source_uri || 'source'}-${index}`} style={styles.description}>
                      - {citation?.source_uri || citation?.label || 'source-uri-unavailable'}
                    </Text>
                  ))
                : null}
            </View>
          ) : null}

          <TouchableOpacity
            testID="player-back-home-button"
            style={styles.backButton}
            onPress={() => navigation.goBack()}
            accessibilityRole="button"
            accessibilityLabel="Back to home"
            accessibilityHint="Returns to the lecture library"
          >
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
