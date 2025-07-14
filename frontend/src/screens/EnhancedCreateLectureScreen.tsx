/**
 * Enhanced Create Lecture Screen - Multi-provider lecture creation with cost optimization
 * Week 2: Integrated cost analysis and intelligent provider selection
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Switch,
  Modal,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useAuth } from '../contexts/AuthContext';
import multiProviderAIService, {
  MultiProviderLectureRequest,
  LectureResponse,
  QualityTier,
  LLMProvider,
  TTSProvider,
} from '../services/multiProviderAI';
import CostOptimizerWidget from '../components/CostOptimizerWidget';

// Navigation types
type RootStackParamList = {
  Home: undefined;
  CreateLecture: undefined;
  EnhancedCreateLecture: undefined;
  LecturePlayer: { lectureId: string };
  Settings: undefined;
};

type CreateLectureNavigationProp = StackNavigationProp<RootStackParamList, 'EnhancedCreateLecture'>;

// Form constants
const DIFFICULTY_OPTIONS = [
  { value: 'beginner', label: 'Beginner', description: 'Clear explanations, basic concepts' },
  { value: 'intermediate', label: 'Intermediate', description: 'Balanced detail and complexity' },
  { value: 'advanced', label: 'Advanced', description: 'Technical depth, expert-level' },
] as const;

const QUALITY_TIERS = [
  { value: 'free', label: 'Free Tier', description: 'Best free providers, limited features' },
  { value: 'standard', label: 'Standard', description: 'Balanced cost and quality' },
  { value: 'premium', label: 'Premium', description: 'Highest quality, advanced features' },
] as const;

const DURATION_PRESETS = [5, 10, 15, 20, 30, 45, 60];

const EnhancedCreateLectureScreen: React.FC = () => {
  const navigation = useNavigation<CreateLectureNavigationProp>();
  const { user } = useAuth();
  
  // Form state
  const [formData, setFormData] = useState<MultiProviderLectureRequest>({
    topic: '',
    duration: 15,
    difficulty: 'beginner',
    quality_tier: 'standard',
    use_cost_optimization: true,
  });
  
  // Selected providers (from cost optimizer)
  const [selectedLLMProvider, setSelectedLLMProvider] = useState<LLMProvider | undefined>();
  const [selectedTTSProvider, setSelectedTTSProvider] = useState<TTSProvider | undefined>();
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);
  const [showCostOptimizer, setShowCostOptimizer] = useState(false);
  
  // Auto-show cost optimizer when topic is entered
  useEffect(() => {
    if (formData.topic.length >= 3) {
      setShowCostOptimizer(true);
    } else {
      setShowCostOptimizer(false);
    }
  }, [formData.topic]);

  // Get estimated cost when form changes
  useEffect(() => {
    if (formData.topic.length >= 3 && formData.duration > 0) {
      getCostEstimate();
    }
  }, [formData.topic, formData.duration, selectedLLMProvider, selectedTTSProvider]);

  const getCostEstimate = async () => {
    try {
      const response = await multiProviderAIService.estimateCost(
        formData.topic,
        formData.duration,
        selectedLLMProvider,
        selectedTTSProvider
      );
      
      if (response.success && response.data) {
        setEstimatedCost(response.data.estimated_cost);
      }
    } catch (error) {
      console.error('Cost estimation error:', error);
    }
  };

  const handleCreateLecture = async () => {
    // Validation
    if (!formData.topic.trim()) {
      Alert.alert('Error', 'Please enter a topic for your lecture');
      return;
    }

    if (formData.topic.length < 3) {
      Alert.alert('Error', 'Topic must be at least 3 characters long');
      return;
    }

    if (formData.duration < 5 || formData.duration > 60) {
      Alert.alert('Error', 'Duration must be between 5 and 60 minutes');
      return;
    }

    setIsLoading(true);

    try {
      // Prepare request with selected providers
      const request: MultiProviderLectureRequest = {
        ...formData,
        preferred_llm_provider: selectedLLMProvider,
        preferred_tts_provider: selectedTTSProvider,
      };

      const response = await multiProviderAIService.generateLecture(request);

      if (response.success && response.data) {
        const lecture = response.data;
        
        // Show success with cost information
        Alert.alert(
          '🎉 Lecture Created Successfully!',
          `Title: ${lecture.title}\n\n` +
          `Providers Used:\n` +
          `• LLM: ${lecture.llm_provider_used.replace('_', ' ').toUpperCase()}\n` +
          `• TTS: ${lecture.tts_provider_used.replace('_', ' ').toUpperCase()}\n\n` +
          `Cost: $${lecture.actual_cost.toFixed(3)}\n` +
          `Savings: $${lecture.cost_savings.toFixed(3)}\n\n` +
          `Ready to play!`,
          [
            {
              text: 'Play Now',
              onPress: () => navigation.navigate('LecturePlayer', { lectureId: lecture.id }),
            },
            {
              text: 'Create Another',
              onPress: () => {
                // Reset form
                setFormData({
                  topic: '',
                  duration: 15,
                  difficulty: 'beginner',
                  quality_tier: 'standard',
                  use_cost_optimization: true,
                });
                setSelectedLLMProvider(undefined);
                setSelectedTTSProvider(undefined);
                setEstimatedCost(null);
              },
            },
          ]
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to create lecture');
      }
    } catch (error) {
      console.error('Lecture creation error:', error);
      Alert.alert('Error', 'Network error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderSelected = (llm: LLMProvider, tts: TTSProvider) => {
    setSelectedLLMProvider(llm);
    setSelectedTTSProvider(tts);
  };

  const renderFormField = (label: string, children: React.ReactNode, required = false) => (
    <View style={styles.formField}>
      <Text style={styles.fieldLabel}>
        {label} {required && <Text style={styles.required}>*</Text>}
      </Text>
      {children}
    </View>
  );

  const renderDifficultySelector = () => (
    <View style={styles.optionGrid}>
      {DIFFICULTY_OPTIONS.map((option) => (
        <TouchableOpacity
          key={option.value}
          style={[
            styles.optionButton,
            formData.difficulty === option.value && styles.selectedOption,
          ]}
          onPress={() => setFormData({ ...formData, difficulty: option.value })}
        >
          <Text style={[
            styles.optionText,
            formData.difficulty === option.value && styles.selectedOptionText,
          ]}>
            {option.label}
          </Text>
          <Text style={styles.optionDescription}>{option.description}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderQualityTierSelector = () => (
    <View style={styles.optionGrid}>
      {QUALITY_TIERS.map((tier) => (
        <TouchableOpacity
          key={tier.value}
          style={[
            styles.optionButton,
            formData.quality_tier === tier.value && styles.selectedOption,
          ]}
          onPress={() => setFormData({ ...formData, quality_tier: tier.value as QualityTier })}
        >
          <Text style={[
            styles.optionText,
            formData.quality_tier === tier.value && styles.selectedOptionText,
          ]}>
            {tier.label}
          </Text>
          <Text style={styles.optionDescription}>{tier.description}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderDurationSelector = () => (
    <View>
      <View style={styles.durationPresets}>
        {DURATION_PRESETS.map((duration) => (
          <TouchableOpacity
            key={duration}
            style={[
              styles.durationButton,
              formData.duration === duration && styles.selectedDuration,
            ]}
            onPress={() => setFormData({ ...formData, duration })}
          >
            <Text style={[
              styles.durationText,
              formData.duration === duration && styles.selectedDurationText,
            ]}>
              {duration}m
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <TextInput
        style={styles.durationInput}
        placeholder="Custom duration (5-60 minutes)"
        value={formData.duration.toString()}
        onChangeText={(text) => {
          const duration = parseInt(text) || 15;
          setFormData({ ...formData, duration });
        }}
        keyboardType="numeric"
      />
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🚀 Enhanced Lecture Creation</Text>
        <Text style={styles.subtitle}>AI-powered content with cost optimization</Text>
      </View>

      {/* Topic Input */}
      {renderFormField(
        'Lecture Topic',
        <TextInput
          style={styles.topicInput}
          placeholder="e.g., Introduction to Machine Learning"
          value={formData.topic}
          onChangeText={(text) => setFormData({ ...formData, topic: text })}
          multiline
          numberOfLines={3}
        />,
        true
      )}

      {/* Duration Selection */}
      {renderFormField('Duration', renderDurationSelector(), true)}

      {/* Difficulty Selection */}
      {renderFormField('Difficulty Level', renderDifficultySelector(), true)}

      {/* Quality Tier Selection */}
      {renderFormField('Quality Tier', renderQualityTierSelector(), true)}

      {/* Cost Optimization Toggle */}
      <View style={styles.toggleContainer}>
        <View style={styles.toggleInfo}>
          <Text style={styles.toggleLabel}>Smart Cost Optimization</Text>
          <Text style={styles.toggleDescription}>
            Automatically select best value providers
          </Text>
        </View>
        <Switch
          value={formData.use_cost_optimization}
          onValueChange={(value) => setFormData({ ...formData, use_cost_optimization: value })}
          trackColor={{ false: '#e5e7eb', true: '#10b981' }}
          thumbColor={formData.use_cost_optimization ? '#ffffff' : '#9ca3af'}
        />
      </View>

      {/* Cost Optimizer Widget */}
      {showCostOptimizer && (
        <CostOptimizerWidget
          topic={formData.topic}
          duration={formData.duration}
          difficulty={formData.difficulty}
          qualityTier={formData.quality_tier}
          onProviderSelected={handleProviderSelected}
        />
      )}

      {/* Estimated Cost Display */}
      {estimatedCost !== null && (
        <View style={styles.costEstimateContainer}>
          <Text style={styles.costEstimateLabel}>Estimated Cost:</Text>
          <Text style={[
            styles.costEstimateValue,
            { color: estimatedCost === 0 ? '#10b981' : '#1f2937' }
          ]}>
            {estimatedCost === 0 ? 'FREE' : `$${estimatedCost.toFixed(3)}`}
          </Text>
        </View>
      )}

      {/* Advanced Options */}
      <TouchableOpacity
        style={styles.advancedToggle}
        onPress={() => setShowAdvancedOptions(!showAdvancedOptions)}
      >
        <Text style={styles.advancedToggleText}>
          {showAdvancedOptions ? '▼' : '▶'} Advanced Options
        </Text>
      </TouchableOpacity>

      {showAdvancedOptions && (
        <View style={styles.advancedOptions}>
          <Text style={styles.advancedTitle}>Provider Selection:</Text>
          
          {selectedLLMProvider && (
            <View style={styles.selectedProvider}>
              <Text style={styles.providerLabel}>LLM Provider:</Text>
              <Text style={styles.providerValue}>
                {selectedLLMProvider.replace('_', ' ').toUpperCase()}
              </Text>
            </View>
          )}
          
          {selectedTTSProvider && (
            <View style={styles.selectedProvider}>
              <Text style={styles.providerLabel}>TTS Provider:</Text>
              <Text style={styles.providerValue}>
                {selectedTTSProvider.replace('_', ' ').toUpperCase()}
              </Text>
            </View>
          )}

          {(!selectedLLMProvider || !selectedTTSProvider) && (
            <Text style={styles.providerHint}>
              💡 Enter a topic above to see provider recommendations
            </Text>
          )}
        </View>
      )}

      {/* Create Button */}
      <TouchableOpacity
        style={[
          styles.createButton,
          (isLoading || !formData.topic.trim()) && styles.createButtonDisabled,
        ]}
        onPress={handleCreateLecture}
        disabled={isLoading || !formData.topic.trim()}
      >
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color="white" size="small" />
            <Text style={styles.createButtonText}>Creating Lecture...</Text>
          </View>
        ) : (
          <Text style={styles.createButtonText}>🎯 Create Enhanced Lecture</Text>
        )}
      </TouchableOpacity>

      {/* Help Text */}
      <View style={styles.helpContainer}>
        <Text style={styles.helpTitle}>💡 Tips for Better Lectures:</Text>
        <Text style={styles.helpText}>
          • Be specific with your topic for better content{'\n'}
          • Free tier available for Google TTS (4M chars/month){'\n'}
          • Cost optimization can save up to 90%{'\n'}
          • Premium tier uses best available models
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  formField: {
    backgroundColor: 'white',
    padding: 20,
    marginVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  fieldLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
  },
  required: {
    color: '#ef4444',
  },
  topicInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9fafb',
    textAlignVertical: 'top',
    minHeight: 80,
  },
  optionGrid: {
    flexDirection: 'column',
    gap: 10,
  },
  optionButton: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 15,
    backgroundColor: '#f9fafb',
  },
  selectedOption: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  optionText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 4,
  },
  selectedOptionText: {
    color: '#3b82f6',
  },
  optionDescription: {
    fontSize: 12,
    color: '#6b7280',
  },
  durationPresets: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 15,
  },
  durationButton: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 6,
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: '#f9fafb',
  },
  selectedDuration: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  durationText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
  },
  selectedDurationText: {
    color: '#3b82f6',
  },
  durationInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9fafb',
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 20,
    marginVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  toggleInfo: {
    flex: 1,
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 4,
  },
  toggleDescription: {
    fontSize: 12,
    color: '#6b7280',
  },
  costEstimateContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f0f9ff',
    padding: 15,
    marginVertical: 5,
    borderWidth: 1,
    borderColor: '#0ea5e9',
    borderRadius: 8,
    marginHorizontal: 20,
  },
  costEstimateLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0369a1',
  },
  costEstimateValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  advancedToggle: {
    backgroundColor: 'white',
    padding: 15,
    marginVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  advancedToggleText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#6b7280',
  },
  advancedOptions: {
    backgroundColor: '#f9fafb',
    padding: 20,
    marginVertical: 5,
  },
  advancedTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
  },
  selectedProvider: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  providerLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  providerValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  providerHint: {
    fontSize: 12,
    color: '#6b7280',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 10,
  },
  createButton: {
    backgroundColor: '#3b82f6',
    margin: 20,
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#3b82f6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  createButtonDisabled: {
    backgroundColor: '#9ca3af',
    shadowOpacity: 0,
    elevation: 0,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  createButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  helpContainer: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  helpTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0369a1',
    marginBottom: 8,
  },
  helpText: {
    fontSize: 12,
    color: '#0369a1',
    lineHeight: 16,
  },
});

export default EnhancedCreateLectureScreen;
