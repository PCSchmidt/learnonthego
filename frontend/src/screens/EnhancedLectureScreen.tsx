import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity, 
  TextInput,
  Alert,
  ActivityIndicator 
} from 'react-native';
import { api } from '../services/api';

interface TTSProvider {
  name: string;
  cost_per_million_chars: number;
  free_tier_chars: number;
  quality_score: number;
  best_for: string;
  features: string[];
}

interface CostComparison {
  total_cost: number;
  free_characters: number;
  paid_characters: number;
  quality_score: number;
}

interface EnhancedLectureRequest {
  topic: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  voice_id: string;
  quality_tier: 'free' | 'standard' | 'premium';
  provider_preference?: string;
  language: string;
}

const EnhancedLectureScreen: React.FC = () => {
  const [providers, setProviders] = useState<Record<string, TTSProvider>>({});
  const [costComparison, setCostComparison] = useState<Record<string, CostComparison>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [estimatedCharCount, setEstimatedCharCount] = useState(5000);
  
  // Form state
  const [lectureForm, setLectureForm] = useState<EnhancedLectureRequest>({
    topic: '',
    duration: 10,
    difficulty: 'intermediate',
    voice_id: 'default',
    quality_tier: 'standard',
    language: 'en'
  });

  useEffect(() => {
    loadProviders();
    loadCostComparison();
  }, [estimatedCharCount]);

  const loadProviders = async () => {
    try {
      const response = await api.get('/api/lectures/tts-providers');
      setProviders(response.data.providers);
    } catch (error) {
      console.error('Failed to load TTS providers:', error);
    }
  };

  const loadCostComparison = async () => {
    try {
      const response = await api.get(`/api/lectures/cost-comparison/${estimatedCharCount}`);
      setCostComparison(response.data.provider_comparison);
    } catch (error) {
      console.error('Failed to load cost comparison:', error);
    }
  };

  const generateEnhancedLecture = async () => {
    if (!lectureForm.topic.trim()) {
      Alert.alert('Error', 'Please enter a topic');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post('/api/lectures/generate-enhanced', lectureForm);
      
      if (response.data.success) {
        Alert.alert(
          'Lecture Generated! 🎉',
          `Provider: ${response.data.provider_used}\n` +
          `Cost: $${response.data.estimated_cost?.toFixed(4) || '0.0000'}\n` +
          `Characters: ${response.data.character_count?.toLocaleString()}\n` +
          `${response.data.was_cached ? '✅ Used cached audio (no cost!)' : '🆕 Newly generated'}`
        );
      }
    } catch (error: any) {
      Alert.alert('Generation Failed', error.response?.data?.detail || 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCost = (cost: number) => {
    if (cost === 0) return 'FREE';
    if (cost < 0.01) return `$${cost.toFixed(4)}`;
    return `$${cost.toFixed(2)}`;
  };

  const getQualityColor = (score: number) => {
    if (score >= 4.5) return '#4CAF50'; // Green for excellent
    if (score >= 4.0) return '#FF9800'; // Orange for good
    return '#757575'; // Gray for basic
  };

  const renderProviderCard = (providerId: string, provider: TTSProvider) => (
    <View key={providerId} style={styles.providerCard}>
      <View style={styles.providerHeader}>
        <Text style={styles.providerName}>{provider.name}</Text>
        <View style={[styles.qualityBadge, { backgroundColor: getQualityColor(provider.quality_score) }]}>
          <Text style={styles.qualityScore}>{provider.quality_score}/5</Text>
        </View>
      </View>
      
      <Text style={styles.providerCost}>
        {formatCost(provider.cost_per_million_chars)} per million chars
      </Text>
      
      {provider.free_tier_chars > 0 && (
        <Text style={styles.freeTier}>
          🎁 {(provider.free_tier_chars / 1_000_000).toFixed(1)}M chars free/month
        </Text>
      )}
      
      <Text style={styles.providerBestFor}>{provider.best_for}</Text>
      
      <View style={styles.features}>
        {provider.features.map((feature, index) => (
          <Text key={index} style={styles.feature}>• {feature}</Text>
        ))}
      </View>
      
      {costComparison[providerId] && (
        <View style={styles.costEstimate}>
          <Text style={styles.costEstimateText}>
            For {estimatedCharCount.toLocaleString()} chars: {formatCost(costComparison[providerId].total_cost)}
          </Text>
        </View>
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🚀 Enhanced Lecture Generation</Text>
      <Text style={styles.subtitle}>Smart TTS with Cost Optimization</Text>
      
      {/* Cost Estimator */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💰 Cost Estimator</Text>
        <View style={styles.estimatorRow}>
          <Text style={styles.label}>Estimated Characters:</Text>
          <TextInput
            style={styles.numberInput}
            value={estimatedCharCount.toString()}
            onChangeText={(text) => setEstimatedCharCount(parseInt(text) || 5000)}
            keyboardType="numeric"
            placeholder="5000"
          />
        </View>
      </View>

      {/* Lecture Generation Form */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📚 Generate Lecture</Text>
        
        <TextInput
          style={styles.textInput}
          placeholder="Enter your topic (e.g., 'Introduction to Machine Learning')"
          value={lectureForm.topic}
          onChangeText={(text) => setLectureForm({...lectureForm, topic: text})}
          multiline
        />
        
        <View style={styles.row}>
          <View style={styles.halfWidth}>
            <Text style={styles.label}>Duration (minutes):</Text>
            <TextInput
              style={styles.numberInput}
              value={lectureForm.duration.toString()}
              onChangeText={(text) => setLectureForm({...lectureForm, duration: parseInt(text) || 10})}
              keyboardType="numeric"
            />
          </View>
          
          <View style={styles.halfWidth}>
            <Text style={styles.label}>Quality Tier:</Text>
            <View style={styles.tierSelector}>
              {(['free', 'standard', 'premium'] as const).map((tier) => (
                <TouchableOpacity
                  key={tier}
                  style={[
                    styles.tierButton,
                    lectureForm.quality_tier === tier && styles.tierButtonActive
                  ]}
                  onPress={() => setLectureForm({...lectureForm, quality_tier: tier})}
                >
                  <Text style={[
                    styles.tierButtonText,
                    lectureForm.quality_tier === tier && styles.tierButtonTextActive
                  ]}>
                    {tier.charAt(0).toUpperCase() + tier.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
        
        <TouchableOpacity
          style={[styles.generateButton, isLoading && styles.generateButtonDisabled]}
          onPress={generateEnhancedLecture}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.generateButtonText}>Generate Enhanced Lecture 🎯</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Provider Comparison */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏆 TTS Provider Comparison</Text>
        <Text style={styles.sectionSubtitle}>
          Smart selection based on cost, quality, and your needs
        </Text>
        
        {Object.entries(providers).map(([providerId, provider]) =>
          renderProviderCard(providerId, provider)
        )}
      </View>

      {/* Cost Optimization Tips */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💡 Cost Optimization Tips</Text>
        <View style={styles.tipsList}>
          <Text style={styles.tip}>• Use caching to avoid duplicate TTS costs</Text>
          <Text style={styles.tip}>• Start with free tiers (Google: 4M chars/month)</Text>
          <Text style={styles.tip}>• Choose Unreal Speech for English content (90% cheaper)</Text>
          <Text style={styles.tip}>• Use OpenAI TTS for multilingual (6-10x cheaper than ElevenLabs)</Text>
          <Text style={styles.tip}>• Optimize text length before generation</Text>
          <Text style={styles.tip}>• Monitor usage to stay within free limits</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  estimatorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  label: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    minWidth: 100,
    textAlign: 'center',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    marginBottom: 16,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  halfWidth: {
    flex: 0.48,
  },
  tierSelector: {
    flexDirection: 'row',
    marginTop: 8,
  },
  tierButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    marginRight: 8,
  },
  tierButtonActive: {
    backgroundColor: '#007AFF',
  },
  tierButtonText: {
    fontSize: 12,
    color: '#333',
  },
  tierButtonTextActive: {
    color: '#fff',
  },
  generateButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  generateButtonDisabled: {
    backgroundColor: '#ccc',
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  providerCard: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  providerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  providerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  qualityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  qualityScore: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  providerCost: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
    marginBottom: 4,
  },
  freeTier: {
    fontSize: 12,
    color: '#4CAF50',
    marginBottom: 4,
  },
  providerBestFor: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
    marginBottom: 8,
  },
  features: {
    marginBottom: 8,
  },
  feature: {
    fontSize: 11,
    color: '#666',
    marginBottom: 2,
  },
  costEstimate: {
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 6,
  },
  costEstimateText: {
    fontSize: 12,
    color: '#333',
    fontWeight: '500',
  },
  tipsList: {
    marginTop: 8,
  },
  tip: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
    paddingLeft: 8,
  },
});

export default EnhancedLectureScreen;
