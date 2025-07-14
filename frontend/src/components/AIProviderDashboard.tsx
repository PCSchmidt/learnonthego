/**
 * AI Provider Dashboard - Central interface for multi-provider management
 * Week 2: Comprehensive dashboard with cost optimization insights
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Dimensions,
  RefreshControl,
} from 'react-native';
import multiProviderAIService, {
  AIProviderDashboardData,
  ProviderStatus,
  QualityTier,
  LLMProvider,
  TTSProvider,
} from '../services/multiProviderAI';

const { width } = Dimensions.get('window');

interface AIProviderDashboardProps {
  onNavigateToLectureCreation?: () => void;
  onNavigateToSettings?: () => void;
}

const AIProviderDashboard: React.FC<AIProviderDashboardProps> = ({
  onNavigateToLectureCreation,
  onNavigateToSettings,
}) => {
  const [dashboardData, setDashboardData] = useState<AIProviderDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard data
  const loadDashboardData = useCallback(async (showLoader = true) => {
    if (showLoader) setIsLoading(true);
    setError(null);

    try {
      const response = await multiProviderAIService.getDashboardData();
      
      if (response.success && response.data) {
        setDashboardData(response.data);
      } else {
        setError(response.error || 'Failed to load dashboard data');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Dashboard loading error:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    loadDashboardData(false);
  }, [loadDashboardData]);

  const handleProviderTest = async (providerType: 'llm' | 'tts', providerName: string) => {
    try {
      const response = await multiProviderAIService.testProvider(providerType, providerName);
      
      if (response.success) {
        Alert.alert('✅ Provider Test', `${providerName} is working correctly`);
        // Refresh data to show updated status
        handleRefresh();
      } else {
        Alert.alert('❌ Provider Test Failed', response.error || 'Unknown error');
      }
    } catch (err) {
      Alert.alert('❌ Test Error', 'Failed to test provider connectivity');
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy': return '#10b981';
      case 'degraded': return '#f59e0b';
      case 'down': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'degraded': return '🟡';
      case 'down': return '🔴';
      default: return '⚪';
    }
  };

  const renderProviderCard = (provider: ProviderStatus) => (
    <View key={provider.provider} style={styles.providerCard}>
      <View style={styles.providerHeader}>
        <View style={styles.providerInfo}>
          <Text style={styles.providerName}>{provider.provider}</Text>
          <View style={styles.statusContainer}>
            <Text style={styles.statusIcon}>{getStatusIcon(provider.status)}</Text>
            <Text style={[styles.statusText, { color: getStatusColor(provider.status) }]}>
              {provider.status.toUpperCase()}
            </Text>
          </View>
        </View>
        <TouchableOpacity
          style={styles.testButton}
          onPress={() => handleProviderTest(
            provider.provider.includes('gpt') || provider.provider.includes('claude') ? 'llm' : 'tts',
            provider.provider
          )}
        >
          <Text style={styles.testButtonText}>Test</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.providerStats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Response Time</Text>
          <Text style={styles.statValue}>{provider.response_time}ms</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Error Rate</Text>
          <Text style={styles.statValue}>{(provider.error_rate * 100).toFixed(1)}%</Text>
        </View>
      </View>
      
      <View style={styles.capabilitiesContainer}>
        <Text style={styles.capabilitiesLabel}>Capabilities:</Text>
        <View style={styles.capabilitiesGrid}>
          {provider.capabilities.map((capability, index) => (
            <View key={index} style={styles.capabilityTag}>
              <Text style={styles.capabilityText}>{capability}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );

  const renderUsageStats = () => {
    if (!dashboardData?.usage_statistics) return null;

    const stats = dashboardData.usage_statistics;
    
    return (
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>📊 Usage Statistics</Text>
        
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats.total_lectures}</Text>
            <Text style={styles.statLabel}>Total Lectures</Text>
          </View>
          
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>${stats.total_cost.toFixed(2)}</Text>
            <Text style={styles.statLabel}>Total Cost</Text>
          </View>
          
          <View style={[styles.statCard, styles.savingsCard]}>
            <Text style={[styles.statNumber, styles.savingsNumber]}>
              ${stats.total_savings.toFixed(2)}
            </Text>
            <Text style={styles.statLabel}>Total Savings</Text>
          </View>
          
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>${stats.average_cost_per_lecture.toFixed(3)}</Text>
            <Text style={styles.statLabel}>Avg Cost/Lecture</Text>
          </View>
        </View>
      </View>
    );
  };

  const renderQuickActions = () => (
    <View style={styles.quickActionsContainer}>
      <Text style={styles.sectionTitle}>⚡ Quick Actions</Text>
      
      <View style={styles.actionButtonsGrid}>
        <TouchableOpacity
          style={[styles.actionButton, styles.primaryAction]}
          onPress={onNavigateToLectureCreation}
        >
          <Text style={styles.actionButtonText}>🎯 Create Lecture</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryAction]}
          onPress={onNavigateToSettings}
        >
          <Text style={styles.actionButtonText}>⚙️ AI Settings</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.tertiaryAction]}
          onPress={handleRefresh}
        >
          <Text style={styles.actionButtonText}>🔄 Refresh Status</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.tertiaryAction]}
          onPress={() => Alert.alert('💡 Cost Tips', 
            '• Google Standard TTS: 4M chars FREE/month\n' +
            '• Unreal Speech: 90% cheaper than premium\n' +
            '• Smart caching prevents duplicate costs\n' +
            '• Free tier automatically selected when available'
          )}
        >
          <Text style={styles.actionButtonText}>💡 Cost Tips</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>Loading AI Providers...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => loadDashboardData()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>🤖 AI Provider Dashboard</Text>
        <Text style={styles.subtitle}>Multi-provider cost optimization system</Text>
      </View>

      {renderUsageStats()}
      {renderQuickActions()}

      <View style={styles.providersContainer}>
        <Text style={styles.sectionTitle}>🔧 Provider Status</Text>
        {dashboardData?.provider_status.map(renderProviderCard)}
      </View>

      {dashboardData?.user_preferences && (
        <View style={styles.preferencesContainer}>
          <Text style={styles.sectionTitle}>⚙️ Current Preferences</Text>
          <View style={styles.preferenceCard}>
            <Text style={styles.preferenceLabel}>Quality Tier:</Text>
            <Text style={styles.preferenceValue}>
              {dashboardData.user_preferences.preferred_quality_tier.toUpperCase()}
            </Text>
          </View>
          <View style={styles.preferenceCard}>
            <Text style={styles.preferenceLabel}>Cost Optimization:</Text>
            <Text style={[
              styles.preferenceValue,
              { color: dashboardData.user_preferences.auto_optimize_costs ? '#10b981' : '#ef4444' }
            ]}>
              {dashboardData.user_preferences.auto_optimize_costs ? 'ENABLED' : 'DISABLED'}
            </Text>
          </View>
          {dashboardData.user_preferences.max_cost_per_lecture && (
            <View style={styles.preferenceCard}>
              <Text style={styles.preferenceLabel}>Max Cost/Lecture:</Text>
              <Text style={styles.preferenceValue}>
                ${dashboardData.user_preferences.max_cost_per_lecture.toFixed(2)}
              </Text>
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#6b7280',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#ef4444',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
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
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 15,
  },
  statsContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginVertical: 10,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: '#f9fafb',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    alignItems: 'center',
  },
  savingsCard: {
    backgroundColor: '#ecfdf5',
    borderWidth: 1,
    borderColor: '#10b981',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  savingsNumber: {
    color: '#10b981',
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  quickActionsContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginVertical: 10,
  },
  actionButtonsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    alignItems: 'center',
  },
  primaryAction: {
    backgroundColor: '#3b82f6',
  },
  secondaryAction: {
    backgroundColor: '#8b5cf6',
  },
  tertiaryAction: {
    backgroundColor: '#10b981',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  providersContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginVertical: 10,
  },
  providerCard: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  providerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  providerInfo: {
    flex: 1,
  },
  providerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    fontSize: 12,
    marginRight: 5,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  testButton: {
    backgroundColor: '#6b7280',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  testButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  providerStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 10,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 2,
  },
  capabilitiesContainer: {
    marginTop: 10,
  },
  capabilitiesLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 5,
  },
  capabilitiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  capabilityTag: {
    backgroundColor: '#e5e7eb',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 5,
    marginBottom: 5,
  },
  capabilityText: {
    fontSize: 10,
    color: '#374151',
  },
  preferencesContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginVertical: 10,
  },
  preferenceCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  preferenceLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  preferenceValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
  },
});

export default AIProviderDashboard;
