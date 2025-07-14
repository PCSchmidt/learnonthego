/**
 * Cost Optimizer Widget - Real-time cost analysis and provider recommendations
 * Week 2: Intelligent cost optimization with live estimates
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import multiProviderAIService, {
  CostAnalysis,
  ProviderRecommendation,
  QualityTier,
  LLMProvider,
  TTSProvider,
} from '../services/multiProviderAI';

interface CostOptimizerProps {
  topic: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  qualityTier: QualityTier;
  onProviderSelected?: (llm: LLMProvider, tts: TTSProvider) => void;
  style?: any;
}

const CostOptimizerWidget: React.FC<CostOptimizerProps> = ({
  topic,
  duration,
  difficulty,
  qualityTier,
  onProviderSelected,
  style,
}) => {
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  // Analyze costs when inputs change
  useEffect(() => {
    if (topic && topic.length >= 3 && duration > 0) {
      analyzeCosts();
    }
  }, [topic, duration, difficulty, qualityTier]);

  const analyzeCosts = useCallback(async () => {
    if (!topic || topic.length < 3) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await multiProviderAIService.getCostAnalysis(
        topic,
        duration,
        difficulty,
        qualityTier
      );

      if (response.success && response.data) {
        setCostAnalysis(response.data);
        setSelectedOption(0); // Default to recommended option
      } else {
        setError(response.error || 'Failed to analyze costs');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Cost analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [topic, duration, difficulty, qualityTier]);

  const handleProviderSelection = (recommendation: ProviderRecommendation, index: number) => {
    setSelectedOption(index);
    if (onProviderSelected) {
      onProviderSelected(recommendation.llm_provider, recommendation.tts_provider);
    }
  };

  const formatCost = (cost: number): string => {
    if (cost === 0) return 'FREE';
    if (cost < 0.01) return '<$0.01';
    return `$${cost.toFixed(3)}`;
  };

  const getSavingsColor = (percentage: number): string => {
    if (percentage >= 70) return '#10b981'; // Green
    if (percentage >= 40) return '#f59e0b'; // Amber
    return '#6b7280'; // Gray
  };

  const renderProviderOption = (recommendation: ProviderRecommendation, index: number) => {
    const isSelected = selectedOption === index;
    const isRecommended = index === 0;

    return (
      <TouchableOpacity
        key={index}
        style={[
          styles.providerOption,
          isSelected && styles.selectedOption,
          isRecommended && styles.recommendedOption,
        ]}
        onPress={() => handleProviderSelection(recommendation, index)}
      >
        <View style={styles.optionHeader}>
          <View style={styles.providerNames}>
            <Text style={styles.providerText}>
              {recommendation.llm_provider.replace('_', ' ').toUpperCase()}
            </Text>
            <Text style={styles.providerSubtext}>
              + {recommendation.tts_provider.replace('_', ' ').toUpperCase()}
            </Text>
          </View>
          
          <View style={styles.costContainer}>
            <Text style={[styles.costText, { color: recommendation.estimated_cost === 0 ? '#10b981' : '#1f2937' }]}>
              {formatCost(recommendation.estimated_cost)}
            </Text>
            {isRecommended && (
              <View style={styles.recommendedBadge}>
                <Text style={styles.recommendedText}>BEST</Text>
              </View>
            )}
          </View>
        </View>

        <View style={styles.optionDetails}>
          <View style={styles.qualityIndicator}>
            <Text style={styles.qualityLabel}>Quality Score:</Text>
            <View style={styles.qualityBar}>
              <View 
                style={[
                  styles.qualityFill, 
                  { width: `${recommendation.quality_score}%`, backgroundColor: getSavingsColor(recommendation.quality_score) }
                ]} 
              />
            </View>
            <Text style={styles.qualityValue}>{recommendation.quality_score}%</Text>
          </View>

          <Text style={styles.reasoningText} numberOfLines={2}>
            {recommendation.reasoning}
          </Text>

          {recommendation.cost_breakdown && (
            <View style={styles.costBreakdown}>
              <Text style={styles.breakdownLabel}>Cost Breakdown:</Text>
              <Text style={styles.breakdownText}>
                LLM: {formatCost(recommendation.cost_breakdown.llm_cost)} | 
                TTS: {formatCost(recommendation.cost_breakdown.tts_cost)}
              </Text>
            </View>
          )}
        </View>

        {isSelected && (
          <View style={styles.selectedIndicator}>
            <Text style={styles.selectedText}>✓ Selected</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.loadingContainer, style]}>
        <ActivityIndicator size="small" color="#3498db" />
        <Text style={styles.loadingText}>Analyzing costs...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, styles.errorContainer, style]}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={analyzeCosts}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!costAnalysis) {
    return (
      <View style={[styles.container, styles.emptyContainer, style]}>
        <Text style={styles.emptyText}>💡 Enter topic details to see cost optimization</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      <View style={styles.header}>
        <Text style={styles.title}>💰 Cost Optimizer</Text>
        
        {costAnalysis.potential_savings > 0 && (
          <View style={styles.savingsHighlight}>
            <Text style={styles.savingsText}>
              Save {formatCost(costAnalysis.potential_savings)} 
              ({costAnalysis.savings_percentage.toFixed(0)}%)
            </Text>
          </View>
        )}

        {costAnalysis.free_tier_available && (
          <View style={styles.freeTierBadge}>
            <Text style={styles.freeTierText}>🎉 FREE TIER AVAILABLE</Text>
          </View>
        )}
      </View>

      <View style={styles.optionsContainer}>
        <Text style={styles.optionsTitle}>Provider Options:</Text>
        
        {costAnalysis.all_options.map((recommendation, index) => 
          renderProviderOption(recommendation, index)
        )}
      </View>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={analyzeCosts}
        >
          <Text style={styles.refreshText}>🔄 Refresh Analysis</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.detailsButton}
          onPress={() => {
            const selected = costAnalysis.all_options[selectedOption];
            Alert.alert(
              '📊 Detailed Analysis',
              `Provider: ${selected.llm_provider} + ${selected.tts_provider}\n\n` +
              `Cost: ${formatCost(selected.estimated_cost)}\n` +
              `Quality: ${selected.quality_score}%\n\n` +
              `Reasoning: ${selected.reasoning}\n\n` +
              `LLM Cost: ${formatCost(selected.cost_breakdown.llm_cost)}\n` +
              `TTS Cost: ${formatCost(selected.cost_breakdown.tts_cost)}\n` +
              `Total: ${formatCost(selected.cost_breakdown.total_cost)}`
            );
          }}
        >
          <Text style={styles.detailsText}>📋 View Details</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
  },
  loadingText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#6b7280',
  },
  errorContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  errorText: {
    fontSize: 14,
    color: '#ef4444',
    textAlign: 'center',
    marginBottom: 10,
  },
  retryButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
  },
  retryText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  emptyText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  header: {
    marginBottom: 15,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  savingsHighlight: {
    backgroundColor: '#ecfdf5',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#10b981',
    marginBottom: 5,
  },
  savingsText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#10b981',
    textAlign: 'center',
  },
  freeTierBadge: {
    backgroundColor: '#fef3c7',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  freeTierText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#92400e',
    textAlign: 'center',
  },
  optionsContainer: {
    marginBottom: 15,
  },
  optionsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
  },
  providerOption: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    backgroundColor: '#f9fafb',
  },
  selectedOption: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  recommendedOption: {
    borderColor: '#10b981',
    backgroundColor: '#ecfdf5',
  },
  optionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  providerNames: {
    flex: 1,
  },
  providerText: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  providerSubtext: {
    fontSize: 11,
    color: '#6b7280',
  },
  costContainer: {
    alignItems: 'flex-end',
  },
  costText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  recommendedBadge: {
    backgroundColor: '#10b981',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginTop: 2,
  },
  recommendedText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: 'white',
  },
  optionDetails: {
    marginTop: 5,
  },
  qualityIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  qualityLabel: {
    fontSize: 11,
    color: '#6b7280',
    marginRight: 8,
  },
  qualityBar: {
    flex: 1,
    height: 4,
    backgroundColor: '#e5e7eb',
    borderRadius: 2,
    marginRight: 8,
  },
  qualityFill: {
    height: '100%',
    borderRadius: 2,
  },
  qualityValue: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#374151',
    minWidth: 30,
  },
  reasoningText: {
    fontSize: 11,
    color: '#6b7280',
    lineHeight: 14,
    marginBottom: 5,
  },
  costBreakdown: {
    marginTop: 5,
  },
  breakdownLabel: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#374151',
  },
  breakdownText: {
    fontSize: 10,
    color: '#6b7280',
  },
  selectedIndicator: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  selectedText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#3b82f6',
    textAlign: 'center',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  refreshButton: {
    backgroundColor: '#6b7280',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
    flex: 1,
    marginRight: 5,
  },
  refreshText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  detailsButton: {
    backgroundColor: '#8b5cf6',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
    flex: 1,
    marginLeft: 5,
  },
  detailsText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default CostOptimizerWidget;
