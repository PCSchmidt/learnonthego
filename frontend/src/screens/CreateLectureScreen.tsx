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
  Platform,
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
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />
      <View style={styles.shell}>
        <View style={styles.headerRail}>
          <Text style={styles.eyebrow}>Lecture Composer</Text>
          <Text style={styles.pageTitle}>Create Premium Lecture</Text>
          <Text style={styles.pageSubtitle}>
            Configure topic, depth, voice profile, and provider mode for a high-fidelity lecture output.
          </Text>

          <View style={styles.metaBlock}>
            <Text style={styles.metaLabel}>Signed In As</Text>
            <Text style={styles.metaValue}>{user?.email || 'Unknown account'}</Text>
          </View>
        </View>

        <View style={styles.formPanel}>
          <Text style={styles.label}>Lecture Topic *</Text>
        <TextInput
          style={styles.textInput}
          value={formData.topic}
          onChangeText={(text) => setFormData({...formData, topic: text})}
          placeholder="e.g., Machine Learning Basics, Quantum Physics, History of Rome"
          placeholderTextColor="#7f8492"
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
    top: -100,
    left: -70,
    width: 260,
    height: 260,
    backgroundColor: 'rgba(198, 168, 106, 0.08)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: 90,
    right: -100,
    width: 290,
    height: 290,
    backgroundColor: 'rgba(155, 166, 197, 0.08)',
  },
  shell: {
    width: '100%',
    maxWidth: 1180,
    alignSelf: 'center',
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    borderWidth: 1,
    borderColor: '#242a37',
    backgroundColor: '#0b0d12',
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
  pageTitle: {
    color: '#f4efe4',
    fontSize: 46,
    lineHeight: 50,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 10,
  },
  pageSubtitle: {
    color: '#aeb6c7',
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 22,
  },
  metaBlock: {
    borderTopWidth: 1,
    borderTopColor: '#2a3140',
    paddingTop: 12,
  },
  metaLabel: {
    color: '#7e8798',
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
    marginBottom: 6,
  },
  metaValue: {
    color: '#d6dbe6',
    fontSize: 14,
    fontWeight: '600',
  },
  formPanel: {
    flex: 1.1,
    backgroundColor: '#f2f0ea',
    padding: 20,
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: 8,
    marginTop: 16,
  },
  textInput: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    padding: 16,
    fontSize: 16,
    color: '#0d1119',
    textAlignVertical: 'top',
    minHeight: 80,
  },
  charCount: {
    fontSize: 12,
    color: '#616979',
    textAlign: 'right',
    marginTop: 4,
  },
  durationScroll: {
    marginTop: 8,
  },
  durationButton: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 60,
    alignItems: 'center',
  },
  durationButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  durationButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2f3644',
  },
  durationButtonTextActive: {
    color: '#f2efe8',
  },
  difficultyContainer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  difficultyButton: {
    flex: 1,
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    alignItems: 'center',
  },
  difficultyButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  difficultyButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2f3644',
  },
  difficultyButtonTextActive: {
    color: '#f2efe8',
  },
  infoCard: {
    backgroundColor: '#ece9df',
    padding: 16,
    borderWidth: 1,
    borderColor: '#c3b188',
    marginTop: 20,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#3e3525',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  infoText: {
    fontSize: 14,
    color: '#4f4635',
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#d7bf89',
    borderWidth: 1,
    borderColor: '#a9905d',
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  createButtonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    color: '#11151e',
    fontSize: 14,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  modeCard: {
    marginTop: 16,
    padding: 14,
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
  },
  modeTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  modeSubtle: {
    fontSize: 13,
    color: '#616979',
    marginBottom: 10,
  },
  modeActions: {
    flexDirection: 'row',
    gap: 8,
  },
  modeButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#939aa8',
    paddingVertical: 10,
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  modeButtonText: {
    color: '#2f3644',
    fontWeight: '600',
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  modeButtonTextActive: {
    color: '#f2efe8',
  },
  // Voice Selection Styles
  voiceScroll: {
    marginTop: 8,
  },
  voiceButton: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 140,
    alignItems: 'center',
  },
  voiceButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  voiceButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2f3644',
    textAlign: 'center',
  },
  voiceButtonTextActive: {
    color: '#f2efe8',
  },
  // Loading Styles
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  loadingText: {
    color: '#11151e',
    fontSize: 14,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
});

export default CreateLectureScreen;
