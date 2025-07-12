/**
 * CreateLectureScreen - Form for creating new lectures
 * Phase 0: Basic text input for topic-based lecture generation
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

interface LectureRequest {
  topic: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  voice: string;
}

const CreateLectureScreen: React.FC = () => {
  const navigation = useNavigation();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<LectureRequest>({
    topic: '',
    duration: 15,
    difficulty: 'beginner',
    voice: 'default',
  });

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
      const response = await fetch(
        'https://learnonthego-production.up.railway.app/api/lectures/generate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const lecture = await response.json();
      
      Alert.alert(
        'Lecture Created!',
        `"${lecture.title}" has been generated successfully.\n\nThis is a Phase 0 mock response. In Phase 1, you'll get real audio lectures!`,
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      console.error('Error creating lecture:', error);
      Alert.alert(
        'Error',
        'Failed to create lecture. Please check your connection and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const difficulties = [
    {label: 'Beginner', value: 'beginner'},
    {label: 'Intermediate', value: 'intermediate'},
    {label: 'Advanced', value: 'advanced'},
  ];

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
              key={diff.value}
              style={[
                styles.difficultyButton,
                formData.difficulty === diff.value && styles.difficultyButtonActive,
              ]}
              onPress={() => setFormData({...formData, difficulty: diff.value as any})}>
              <Text
                style={[
                  styles.difficultyButtonText,
                  formData.difficulty === diff.value && styles.difficultyButtonTextActive,
                ]}>
                {diff.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>Phase 0 - Proof of Concept</Text>
          <Text style={styles.infoText}>
            This will generate a mock lecture response. In Phase 1, we'll add:
            {'\n'}• Real AI-generated content
            {'\n'}• Text-to-speech conversion
            {'\n'}• Audio file downloads
            {'\n'}• PDF document processing
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.createButton, isLoading && styles.createButtonDisabled]}
          onPress={handleCreateLecture}
          disabled={isLoading}>
          {isLoading ? (
            <ActivityIndicator color="#ffffff" />
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
    fontWeight: 'bold',
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
    fontWeight: 'bold',
  },
});

export default CreateLectureScreen;
