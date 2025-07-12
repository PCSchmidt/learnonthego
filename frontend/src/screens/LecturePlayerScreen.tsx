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
} from 'react-native';
import {useNavigation, useRoute} from '@react-navigation/native';

const LecturePlayerScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const lectureId = (route.params as any)?.lectureId || 'unknown';

  return (
    <View style={styles.container}>
      <View style={styles.playerCard}>
        <Text style={styles.title}>Lecture Player</Text>
        <Text style={styles.subtitle}>Lecture ID: {lectureId}</Text>
        
        <View style={styles.placeholder}>
          <Text style={styles.placeholderText}>
            🎵 Audio Player Coming in Phase 1
          </Text>
          <Text style={styles.description}>
            Here you'll be able to:
            {'\n'}• Play/pause lectures
            {'\n'}• Seek through content
            {'\n'}• Adjust playback speed
            {'\n'}• Download for offline listening
          </Text>
        </View>

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>Back to Home</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    padding: 20,
    justifyContent: 'center',
  },
  playerCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 24,
  },
  placeholder: {
    alignItems: 'center',
    marginBottom: 32,
  },
  placeholderText: {
    fontSize: 20,
    color: '#6366f1',
    marginBottom: 16,
    textAlign: 'center',
  },
  description: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  backButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default LecturePlayerScreen;
