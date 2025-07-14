/**
 * Provider Status Indicators - Real-time AI provider health monitoring
 * Week 2: Visual indicators for provider availability and performance
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  ScrollView,
} from 'react-native';
import multiProviderAIService, { ProviderStatus } from '../services/multiProviderAI';

interface ProviderStatusIndicatorProps {
  style?: any;
  showDetails?: boolean;
  onProviderPress?: (provider: ProviderStatus) => void;
}

const ProviderStatusIndicator: React.FC<ProviderStatusIndicatorProps> = ({
  style,
  showDetails = false,
  onProviderPress,
}) => {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<ProviderStatus | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    loadProviderStatus();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadProviderStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadProviderStatus = async () => {
    try {
      const response = await multiProviderAIService.getProviderStatus();
      
      if (response.success && response.data) {
        setProviders(response.data);
        setError(null);
        setLastUpdated(new Date());
      } else {
        setError(response.error || 'Failed to load provider status');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Provider status error:', err);
    } finally {
      setIsLoading(false);
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

  const getProviderDisplayName = (provider: string): string => {
    return provider
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleProviderPress = (provider: ProviderStatus) => {
    if (onProviderPress) {
      onProviderPress(provider);
    } else {
      setSelectedProvider(provider);
      setShowModal(true);
    }
  };

  const getOverallStatus = (): { status: string; color: string; icon: string } => {
    if (providers.length === 0) {
      return { status: 'Unknown', color: '#6b7280', icon: '⚪' };
    }

    const healthyCount = providers.filter(p => p.status === 'healthy').length;
    const totalCount = providers.length;
    const healthyPercentage = (healthyCount / totalCount) * 100;

    if (healthyPercentage >= 80) {
      return { status: 'All Systems Operational', color: '#10b981', icon: '🟢' };
    } else if (healthyPercentage >= 50) {
      return { status: 'Some Issues Detected', color: '#f59e0b', icon: '🟡' };
    } else {
      return { status: 'Major Issues', color: '#ef4444', icon: '🔴' };
    }
  };

  const renderProviderDot = (provider: ProviderStatus, index: number) => (
    <TouchableOpacity
      key={provider.provider}
      style={[
        styles.providerDot,
        { backgroundColor: getStatusColor(provider.status) },
      ]}
      onPress={() => handleProviderPress(provider)}
    >
      {showDetails && (
        <Text style={styles.providerDotText}>
          {getProviderDisplayName(provider.provider).substring(0, 3)}
        </Text>
      )}
    </TouchableOpacity>
  );

  const renderCompactView = () => {
    const overall = getOverallStatus();
    
    return (
      <TouchableOpacity 
        style={[styles.compactContainer, style]}
        onPress={() => setShowModal(true)}
      >
        <View style={styles.compactHeader}>
          <Text style={styles.compactIcon}>{overall.icon}</Text>
          <Text style={[styles.compactStatus, { color: overall.color }]}>
            {overall.status}
          </Text>
        </View>
        
        <View style={styles.providersRow}>
          {providers.slice(0, 6).map(renderProviderDot)}
          {providers.length > 6 && (
            <Text style={styles.moreIndicator}>+{providers.length - 6}</Text>
          )}
        </View>
        
        <Text style={styles.lastUpdated}>
          Updated {lastUpdated.toLocaleTimeString()}
        </Text>
      </TouchableOpacity>
    );
  };

  const renderDetailedView = () => (
    <View style={[styles.detailedContainer, style]}>
      <View style={styles.detailedHeader}>
        <Text style={styles.detailedTitle}>🔧 Provider Status</Text>
        <TouchableOpacity 
          style={styles.refreshButton}
          onPress={loadProviderStatus}
        >
          <Text style={styles.refreshText}>🔄</Text>
        </TouchableOpacity>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.providersGrid}>
          {providers.map((provider, index) => (
            <TouchableOpacity
              key={provider.provider}
              style={styles.providerCard}
              onPress={() => handleProviderPress(provider)}
            >
              <Text style={styles.providerCardIcon}>
                {getStatusIcon(provider.status)}
              </Text>
              <Text style={styles.providerCardName}>
                {getProviderDisplayName(provider.provider)}
              </Text>
              <Text style={[
                styles.providerCardStatus,
                { color: getStatusColor(provider.status) }
              ]}>
                {provider.status.toUpperCase()}
              </Text>
              <Text style={styles.providerCardTime}>
                {provider.response_time}ms
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      <Text style={styles.lastUpdated}>
        Last updated: {lastUpdated.toLocaleTimeString()}
      </Text>
    </View>
  );

  const renderProviderModal = () => (
    <Modal
      visible={showModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowModal(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>
            {selectedProvider ? 
              `${getProviderDisplayName(selectedProvider.provider)} Details` : 
              'Provider Status Overview'
            }
          </Text>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setShowModal(false)}
          >
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          {selectedProvider ? (
            // Single provider details
            <View style={styles.providerDetails}>
              <View style={styles.statusBadge}>
                <Text style={styles.statusBadgeIcon}>
                  {getStatusIcon(selectedProvider.status)}
                </Text>
                <Text style={[
                  styles.statusBadgeText,
                  { color: getStatusColor(selectedProvider.status) }
                ]}>
                  {selectedProvider.status.toUpperCase()}
                </Text>
              </View>

              <View style={styles.metricsGrid}>
                <View style={styles.metricCard}>
                  <Text style={styles.metricLabel}>Response Time</Text>
                  <Text style={styles.metricValue}>{selectedProvider.response_time}ms</Text>
                </View>
                
                <View style={styles.metricCard}>
                  <Text style={styles.metricLabel}>Error Rate</Text>
                  <Text style={styles.metricValue}>
                    {(selectedProvider.error_rate * 100).toFixed(1)}%
                  </Text>
                </View>
                
                <View style={styles.metricCard}>
                  <Text style={styles.metricLabel}>Last Checked</Text>
                  <Text style={styles.metricValue}>
                    {new Date(selectedProvider.last_checked).toLocaleTimeString()}
                  </Text>
                </View>
              </View>

              <View style={styles.capabilitiesSection}>
                <Text style={styles.capabilitiesTitle}>Capabilities:</Text>
                <View style={styles.capabilitiesGrid}>
                  {selectedProvider.capabilities.map((capability, index) => (
                    <View key={index} style={styles.capabilityTag}>
                      <Text style={styles.capabilityText}>{capability}</Text>
                    </View>
                  ))}
                </View>
              </View>
            </View>
          ) : (
            // All providers overview
            <View>
              {providers.map((provider) => (
                <TouchableOpacity
                  key={provider.provider}
                  style={styles.providerListItem}
                  onPress={() => setSelectedProvider(provider)}
                >
                  <View style={styles.providerListInfo}>
                    <Text style={styles.providerListIcon}>
                      {getStatusIcon(provider.status)}
                    </Text>
                    <View style={styles.providerListDetails}>
                      <Text style={styles.providerListName}>
                        {getProviderDisplayName(provider.provider)}
                      </Text>
                      <Text style={[
                        styles.providerListStatus,
                        { color: getStatusColor(provider.status) }
                      ]}>
                        {provider.status} • {provider.response_time}ms
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.chevron}>›</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </ScrollView>
      </View>
    </Modal>
  );

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, style]}>
        <ActivityIndicator size="small" color="#3498db" />
        <Text style={styles.loadingText}>Loading status...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.errorContainer, style]}>
        <Text style={styles.errorText}>❌ {error}</Text>
      </View>
    );
  }

  return (
    <View>
      {showDetails ? renderDetailedView() : renderCompactView()}
      {renderProviderModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  compactContainer: {
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  compactHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  compactIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  compactStatus: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  providersRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  providerDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  providerDotText: {
    fontSize: 6,
    color: 'white',
    fontWeight: 'bold',
  },
  moreIndicator: {
    fontSize: 10,
    color: '#6b7280',
    marginLeft: 4,
  },
  lastUpdated: {
    fontSize: 10,
    color: '#9ca3af',
  },
  detailedContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  detailedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  detailedTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  refreshButton: {
    padding: 5,
  },
  refreshText: {
    fontSize: 16,
  },
  providersGrid: {
    flexDirection: 'row',
    paddingVertical: 10,
  },
  providerCard: {
    backgroundColor: '#f9fafb',
    padding: 10,
    borderRadius: 8,
    marginRight: 10,
    minWidth: 80,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  providerCardIcon: {
    fontSize: 16,
    marginBottom: 4,
  },
  providerCardName: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#374151',
    textAlign: 'center',
    marginBottom: 2,
  },
  providerCardStatus: {
    fontSize: 8,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  providerCardTime: {
    fontSize: 8,
    color: '#6b7280',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 12,
    color: '#6b7280',
  },
  errorContainer: {
    padding: 15,
    backgroundColor: '#fef2f2',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  errorText: {
    fontSize: 12,
    color: '#dc2626',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  closeButton: {
    padding: 5,
  },
  closeText: {
    fontSize: 18,
    color: '#6b7280',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  providerDetails: {
    alignItems: 'center',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 20,
  },
  statusBadgeIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  statusBadgeText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  metricsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
  },
  metricCard: {
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    minWidth: 100,
  },
  metricLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  capabilitiesSection: {
    width: '100%',
  },
  capabilitiesTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 10,
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
  providerListItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  providerListInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  providerListIcon: {
    fontSize: 16,
    marginRight: 12,
  },
  providerListDetails: {
    flex: 1,
  },
  providerListName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 2,
  },
  providerListStatus: {
    fontSize: 12,
    fontWeight: '500',
  },
  chevron: {
    fontSize: 18,
    color: '#9ca3af',
  },
});

export default ProviderStatusIndicator;
