/**
 * CreateLectureScreen - Form for creating new lectures
 * Phase 2d: Integrated with authentication and backend API
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {useNavigation} from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import lectureService, {
  ApiKeyStatus,
  AVAILABLE_VOICES,
  DIFFICULTY_LEVELS,
  LectureRequest,
} from '../services/lecture';
import { StackNavigationProp } from '@react-navigation/stack';

// Navigation types
type RootStackParamList = {
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: { lectureId: string };
  Settings: undefined;
};

type CreateLectureNavigationProp = StackNavigationProp<RootStackParamList, 'CreateLecture'>;

const CreateLectureScreen: React.FC = () => {
  const navigation = useNavigation<CreateLectureNavigationProp>();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isStatusLoading, setIsStatusLoading] = useState(true);
  const [useByok, setUseByok] = useState(true);
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [formData, setFormData] = useState<LectureRequest>({
    topic: '',
    duration: 15,
    difficulty: 'beginner',
    voice: 'Rachel', // Default to first available voice
  });

  React.useEffect(() => {
    const loadKeyStatus = async () => {
      setIsStatusLoading(true);
      const response = await lectureService.getApiKeyStatus();
      if (response.success && response.data) {
        setKeyStatus(response.data);
        setUseByok(response.data.setup_complete);
      }
      setIsStatusLoading(false);
    };

    loadKeyStatus();
  }, []);

  const handleCreateLecture = async () => {
    if (!formData.topic.trim()) {
      Alert.alert('Error', 'Please enter a topic for your lecture');
      return;
    }

    if (formData.topic.length < 3) {
      Alert.alert('Error', 'Topic must be at least 3 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const response = await lectureService.createLecture(formData, {
        useByok,
      });
      
      if (response.success && response.data) {
        const generatedLectureId = response.data.id || `v2-${Date.now()}`;
        const keySource = response.data.key_source === 'user-encrypted-storage'
          ? 'BYOK secure storage'
          : 'environment provider config';

        Alert.alert(
          'Lecture Created',
          `${response.data.title || 'V2 Lecture'} is ready.\n\nDuration: ${formData.duration} minutes\nDifficulty: ${formData.difficulty}\nMode: ${keySource}`,
          [
            {
              text: 'Play Now',
              onPress: () => {
                // Navigate to lecture player
                navigation.navigate('LecturePlayer', { lectureId: generatedLectureId });
              },
            },
            {
              text: 'View Library',
              onPress: () => navigation.navigate('Home'),
            },
          ]
        );
      } else {
        throw new Error(
          response.error ||
            (useByok
              ? 'Failed to create lecture using BYOK path. Verify your provider keys in settings.'
              : 'Failed to create lecture')
        );
      }
    } catch (error) {
      console.error('Error creating lecture:', error);
      Alert.alert(
        'Generation Failed',
        error instanceof Error ? error.message : 'Failed to create lecture. Please check your connection and try again.',
        [
          {
            text: 'Retry',
            onPress: handleCreateLecture,
          },
          {
            text: 'Cancel',
            style: 'cancel',
          },
        ]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const difficulties = DIFFICULTY_LEVELS;
  const voices = AVAILABLE_VOICES;
  const durations = [5, 10, 15, 20, 30, 45, 60];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.label}>Lecture Topic *</Text>
        <TextInput
          style={styles.textInput}
          value={formData.topic}
          onChangeText={(text) => setFormData({...formData, topic: text})}
          placeholder="e.g., Machine Learning Basics, Quantum Physics, History of Rome"
          multiline
          numberOfLines={3}
          maxLength={500}
        />
        <Text style={styles.charCount}>{formData.topic.length}/500</Text>

        <View style={styles.modeCard}>
          <Text style={styles.modeTitle}>Generation Mode</Text>
          {isStatusLoading ? (
            <Text style={styles.modeSubtle}>Checking key status...</Text>
          ) : (
            <>
              <Text style={styles.modeSubtle}>
                {keyStatus?.setup_complete
                  ? 'BYOK keys detected for OpenRouter and ElevenLabs.'
                  : `Missing keys: ${(keyStatus?.missing_keys || []).join(', ') || 'unknown'}`}
              </Text>
              <View style={styles.modeActions}>
                <TouchableOpacity
                  style={[styles.modeButton, useByok && styles.modeButtonActive]}
                  onPress={() => setUseByok(true)}
                  disabled={!keyStatus?.setup_complete}
                >
                  <Text style={[styles.modeButtonText, useByok && styles.modeButtonTextActive]}>
                    BYOK
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modeButton, !useByok && styles.modeButtonActive]}
                  onPress={() => setUseByok(false)}
                >
                  <Text style={[styles.modeButtonText, !useByok && styles.modeButtonTextActive]}>
                    Environment
                  </Text>
                </TouchableOpacity>
              </View>
            </>
          )}
        </View>

        <Text style={styles.label}>Duration (minutes)</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.durationScroll}>
          {durations.map((duration) => (
            <TouchableOpacity
              key={duration}
              style={[
                styles.durationButton,
                formData.duration === duration && styles.durationButtonActive,
              ]}
              onPress={() => setFormData({...formData, duration})}>
              <Text
                style={[
                  styles.durationButtonText,
                  formData.duration === duration && styles.durationButtonTextActive,
                ]}>
                {duration}m
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <Text style={styles.label}>Difficulty Level</Text>
        <View style={styles.difficultyContainer}>
          {difficulties.map((diff) => (
            <TouchableOpacity
              key={diff.id}
              style={[
                styles.difficultyButton,
                formData.difficulty === diff.id && styles.difficultyButtonActive,
              ]}
              onPress={() => setFormData({...formData, difficulty: diff.id as any})}>
              <Text
                style={[
                  styles.difficultyButtonText,
                  formData.difficulty === diff.id && styles.difficultyButtonTextActive,
                ]}>
                {diff.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Voice Selection</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.voiceScroll}>
          {voices.map((voice) => (
            <TouchableOpacity
              key={voice.id}
              style={[
                styles.voiceButton,
                formData.voice === voice.id && styles.voiceButtonActive,
              ]}
              onPress={() => setFormData({...formData, voice: voice.id})}>
              <Text
                style={[
                  styles.voiceButtonText,
                  formData.voice === voice.id && styles.voiceButtonTextActive,
                ]}>
                {voice.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>AI-Powered Lecture Generation</Text>
          <Text style={styles.infoText}>
            Your lecture uses the V2 pipeline with provider abstraction and robust validation.
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.createButton, isLoading && styles.createButtonDisabled]}
          onPress={handleCreateLecture}
          disabled={isLoading}>
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator color="#ffffff" />
              <Text style={styles.loadingText}>Generating your lecture...</Text>
            </View>
          ) : (
            <Text style={styles.createButtonText}>Create Lecture</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  form: {
    padding: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    marginTop: 16,
  },
  textInput: {
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    textAlignVertical: 'top',
    minHeight: 80,
  },
  charCount: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'right',
    marginTop: 4,
  },
  durationScroll: {
    marginTop: 8,
  },
  durationButton: {
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 60,
    alignItems: 'center',
  },
  durationButtonActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  durationButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  durationButtonTextActive: {
    color: '#ffffff',
  },
  difficultyContainer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  difficultyButton: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  difficultyButtonActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  difficultyButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  difficultyButtonTextActive: {
    color: '#ffffff',
  },
  infoCard: {
    backgroundColor: '#eff6ff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#bfdbfe',
    marginTop: 20,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1e40af',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1e40af',
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 24,
    shadowColor: '#6366f1',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  createButtonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  modeCard: {
    marginTop: 16,
    padding: 14,
    borderRadius: 10,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  modeTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 6,
  },
  modeSubtle: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 10,
  },
  modeActions: {
    flexDirection: 'row',
    gap: 8,
  },
  modeButton: {
    flex: 1,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    paddingVertical: 10,
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: '#0f172a',
    borderColor: '#0f172a',
  },
  modeButtonText: {
    color: '#0f172a',
    fontWeight: '600',
    fontSize: 13,
  },
  modeButtonTextActive: {
    color: '#f8fafc',
  },
  // Voice Selection Styles
  voiceScroll: {
    marginTop: 8,
  },
  voiceButton: {
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 140,
    alignItems: 'center',
  },
  voiceButtonActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  voiceButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    textAlign: 'center',
  },
  voiceButtonTextActive: {
    color: '#ffffff',
  },
  // Loading Styles
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default CreateLectureScreen;
