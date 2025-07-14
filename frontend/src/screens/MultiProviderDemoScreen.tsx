/**
 * Multi-Provider Demo Screen - Comprehensive demonstration of Week 2 features
 * Showcases all frontend components working together
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Alert,
} from 'react-native';
import AIProviderDashboard from '../components/AIProviderDashboard';
import CostOptimizerWidget from '../components/CostOptimizerWidget';
import ProviderStatusIndicator from '../components/ProviderStatusIndicator';
import { QualityTier, LLMProvider, TTSProvider } from '../services/multiProviderAI';

const MultiProviderDemoScreen: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState<'dashboard' | 'cost' | 'status'>('dashboard');
  const [demoTopic, setDemoTopic] = useState('Introduction to Machine Learning');
  const [demoDuration, setDemoDuration] = useState(15);
  const [demoQuality, setDemoQuality] = useState<QualityTier>('standard');

  const handleProviderSelected = (llm: LLMProvider, tts: TTSProvider) => {
    Alert.alert(
      '✅ Providers Selected',
      `LLM: ${llm.replace('_', ' ').toUpperCase()}\n` +
      `TTS: ${tts.replace('_', ' ').toUpperCase()}\n\n` +
      'This selection would be used for lecture generation!'
    );
  };

  const handleNavigateToLectureCreation = () => {
    Alert.alert(
      '🎯 Navigate to Lecture Creation',
      'This would navigate to the Enhanced Create Lecture Screen with cost optimization enabled!'
    );
  };

  const handleNavigateToSettings = () => {
    Alert.alert(
      '⚙️ Navigate to AI Settings',
      'This would open AI Provider settings where users can:\n\n' +
      '• Configure preferred providers\n' +
      '• Set cost limits\n' +
      '• Manage API keys\n' +
      '• Adjust quality preferences'
    );
  };

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      <TouchableOpacity
        style={[styles.tab, selectedTab === 'dashboard' && styles.activeTab]}
        onPress={() => setSelectedTab('dashboard')}
      >
        <Text style={[styles.tabText, selectedTab === 'dashboard' && styles.activeTabText]}>
          🤖 Dashboard
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, selectedTab === 'cost' && styles.activeTab]}
        onPress={() => setSelectedTab('cost')}
      >
        <Text style={[styles.tabText, selectedTab === 'cost' && styles.activeTabText]}>
          💰 Cost Optimizer
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, selectedTab === 'status' && styles.activeTab]}
        onPress={() => setSelectedTab('status')}
      >
        <Text style={[styles.tabText, selectedTab === 'status' && styles.activeTabText]}>
          🔧 Status
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderDashboardTab = () => (
    <AIProviderDashboard
      onNavigateToLectureCreation={handleNavigateToLectureCreation}
      onNavigateToSettings={handleNavigateToSettings}
    />
  );

  const renderCostOptimizerTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.demoControls}>
        <Text style={styles.demoTitle}>🧪 Cost Optimizer Demo</Text>
        <Text style={styles.demoDescription}>
          Experience real-time cost analysis and provider recommendations
        </Text>
        
        <View style={styles.demoSettings}>
          <Text style={styles.settingLabel}>Demo Topic: {demoTopic}</Text>
          <Text style={styles.settingLabel}>Duration: {demoDuration} minutes</Text>
          <Text style={styles.settingLabel}>Quality: {demoQuality.toUpperCase()}</Text>
        </View>
        
        <View style={styles.demoButtons}>
          <TouchableOpacity
            style={styles.demoButton}
            onPress={() => setDemoTopic('Advanced React Native Architecture')}
          >
            <Text style={styles.demoButtonText}>Try Technical Topic</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.demoButton}
            onPress={() => setDemoDuration(30)}
          >
            <Text style={styles.demoButtonText}>30 Min Lecture</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.demoButton}
            onPress={() => setDemoQuality('premium')}
          >
            <Text style={styles.demoButtonText}>Premium Quality</Text>
          </TouchableOpacity>
        </View>
      </View>

      <CostOptimizerWidget
        topic={demoTopic}
        duration={demoDuration}
        difficulty="intermediate"
        qualityTier={demoQuality}
        onProviderSelected={handleProviderSelected}
      />

      <View style={styles.demoExplanation}>
        <Text style={styles.explanationTitle}>💡 How Cost Optimization Works:</Text>
        <Text style={styles.explanationText}>
          1. Enter your lecture topic and requirements{'\n'}
          2. AI analyzes content complexity and duration{'\n'}
          3. System compares all available providers{'\n'}
          4. Recommends optimal cost/quality combination{'\n'}
          5. Shows potential savings and reasoning{'\n'}
          6. User can accept or choose alternative
        </Text>
      </View>
    </View>
  );

  const renderStatusTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.statusDemo}>
        <Text style={styles.demoTitle}>🔧 Provider Status Monitoring</Text>
        <Text style={styles.demoDescription}>
          Real-time health monitoring for all AI providers
        </Text>
        
        <View style={styles.statusVariants}>
          <Text style={styles.variantTitle}>Compact View:</Text>
          <ProviderStatusIndicator showDetails={false} />
          
          <Text style={styles.variantTitle}>Detailed View:</Text>
          <ProviderStatusIndicator showDetails={true} />
        </View>
        
        <View style={styles.statusFeatures}>
          <Text style={styles.featuresTitle}>🚀 Status Features:</Text>
          <Text style={styles.featuresText}>
            • Real-time health monitoring{'\n'}
            • Response time tracking{'\n'}
            • Error rate analysis{'\n'}
            • Capability detection{'\n'}
            • Auto-refresh every 30 seconds{'\n'}
            • Interactive provider details{'\n'}
            • Overall system status
          </Text>
        </View>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🚀 Multi-Provider AI Demo</Text>
        <Text style={styles.subtitle}>Week 2: Frontend Integration Complete</Text>
      </View>

      {renderTabBar()}

      <ScrollView style={styles.content}>
        {selectedTab === 'dashboard' && renderDashboardTab()}
        {selectedTab === 'cost' && renderCostOptimizerTab()}
        {selectedTab === 'status' && renderStatusTab()}
      </ScrollView>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          💰 Cost-optimized • 🤖 8 AI providers • 🔧 Real-time monitoring
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
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
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  tab: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#3b82f6',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  activeTabText: {
    color: '#3b82f6',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    padding: 20,
  },
  demoControls: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  demoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  demoDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 15,
  },
  demoSettings: {
    backgroundColor: '#f9fafb',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  settingLabel: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 5,
  },
  demoButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  demoButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    flex: 1,
    marginHorizontal: 2,
  },
  demoButtonText: {
    color: 'white',
    fontSize: 11,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  demoExplanation: {
    backgroundColor: '#f0f9ff',
    padding: 20,
    borderRadius: 12,
    marginTop: 20,
    borderWidth: 1,
    borderColor: '#0ea5e9',
  },
  explanationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0369a1',
    marginBottom: 10,
  },
  explanationText: {
    fontSize: 13,
    color: '#0369a1',
    lineHeight: 18,
  },
  statusDemo: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  statusVariants: {
    marginTop: 20,
  },
  variantTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginTop: 15,
    marginBottom: 10,
  },
  statusFeatures: {
    backgroundColor: '#f9fafb',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  featuresTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 8,
  },
  featuresText: {
    fontSize: 12,
    color: '#6b7280',
    lineHeight: 16,
  },
  footer: {
    backgroundColor: 'white',
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  footerText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
});

export default MultiProviderDemoScreen;
