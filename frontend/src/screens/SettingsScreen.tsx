/**
 * SettingsScreen - App configuration and user preferences
 * Phase 0: Basic settings placeholder
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import lectureService, { ApiKeyStatus } from '../services/lecture';

type ProviderStatusItem = {
  provider: string;
  last_validation_outcome: 'missing' | 'valid' | 'invalid';
  remediation_hint: string;
  validation_error: string | null;
  key_name: string | null;
  last_validation_at: string | null;
};

const SettingsScreen: React.FC = () => {
  const [isKeyStatusLoading, setIsKeyStatusLoading] = useState(true);
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);

  const loadKeyStatus = async () => {
    setIsKeyStatusLoading(true);
    try {
      const response = await lectureService.getApiKeyStatus();
      if (response.success && response.data) {
        setKeyStatus(response.data);
      }
    } finally {
      setIsKeyStatusLoading(false);
    }
  };

  useEffect(() => {
    loadKeyStatus();
  }, []);

  const providerStatusItems: ProviderStatusItem[] = keyStatus?.provider_status
    ? Object.entries(keyStatus.provider_status).map(([provider, state]) => ({
        provider,
        last_validation_outcome: state.last_validation_outcome,
        remediation_hint: state.remediation_hint,
        validation_error: state.validation_error,
        key_name: state.key_name,
        last_validation_at: state.last_validation_at,
      }))
    : ["openrouter", "elevenlabs"].map((provider) => ({
        provider,
        last_validation_outcome: (keyStatus?.missing_keys || []).includes(provider) ? "missing" : "valid",
        remediation_hint: (keyStatus?.missing_keys || []).includes(provider)
          ? `Add your ${provider} key in Settings and run validation.`
          : "Key is valid and ready for generation.",
        validation_error: null,
        key_name: null,
        last_validation_at: null,
      }));

  const formatProviderLabel = (provider: string) =>
    provider === 'openrouter' ? 'OpenRouter' : provider === 'elevenlabs' ? 'ElevenLabs' : provider;

  const getOutcomeLabel = (outcome: ProviderStatusItem['last_validation_outcome']) =>
    outcome === 'valid' ? 'Valid' : outcome === 'invalid' ? 'Invalid' : 'Missing';

  const handleAbout = () => {
    Alert.alert(
      'About LearnOnTheGo',
      'Version 1.0.0 - Phase 0\n\nA mobile-first app for converting text topics into personalized audio lectures.\n\nBuilt with React Native, FastAPI, and Railway.'
    );
  };

  const handleTestConnection = async () => {
    try {
      const response = await fetch('https://learnonthego-production.up.railway.app/health');
      const data = await response.json();
      Alert.alert(
        'Connection Test',
        `✅ Connected to backend\n\nStatus: ${data.status}\nMessage: ${data.message}`
      );
    } catch (error) {
      Alert.alert(
        'Connection Test',
        '❌ Failed to connect to backend\n\nPlease check your internet connection.'
      );
    }
  };

  const settingsItems = [
    {
      title: 'Test API Connection',
      description: 'Check backend connectivity',
      onPress: handleTestConnection,
      icon: '🔗',
    },
    {
      title: 'About',
      description: 'App version and information',
      onPress: handleAbout,
      icon: 'ℹ️',
    },
  ];

  const comingSoonItems = [
    {
      title: 'Account Settings',
      description: 'User profile and preferences',
      icon: '👤',
    },
    {
      title: 'Audio Settings',
      description: 'Voice selection and audio quality',
      icon: '🎵',
    },
    {
      title: 'API Keys',
      description: 'Configure OpenRouter and ElevenLabs',
      icon: '🔑',
    },
    {
      title: 'Storage',
      description: 'Manage downloaded lectures',
      icon: '💾',
    },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />
      <View style={styles.shell}>
        <View style={styles.headerRail}>
          <Text style={styles.eyebrow}>Control Suite</Text>
          <Text style={styles.pageTitle}>Settings</Text>
          <Text style={styles.pageSubtitle}>
            Configure system behavior, validate infrastructure, and manage your account operations.
          </Text>
        </View>

        <View style={styles.panel}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Generation Key Status</Text>
            <View style={styles.statusCard}>
              {isKeyStatusLoading ? (
                <Text testID="settings-key-status-loading" style={styles.statusText}>Checking provider key status...</Text>
              ) : (
                <>
                  <Text testID="settings-byok-status" style={styles.statusText}>
                    {keyStatus?.setup_complete
                      ? 'BYOK ready: OpenRouter and ElevenLabs keys are configured.'
                      : `BYOK not ready: missing ${(keyStatus?.missing_keys || []).join(', ') || 'required provider keys'}.`}
                  </Text>
                  <Text testID="settings-fallback-status" style={styles.statusSubtle}>
                    {keyStatus?.setup_complete
                      ? 'Create screen can use BYOK by default, with environment mode available as manual fallback.'
                      : 'Fallback behavior: generation uses environment-managed providers until BYOK keys are complete.'}
                  </Text>
                  <View style={styles.providerStatusList}>
                    {providerStatusItems.map((item) => (
                      <View key={item.provider} style={styles.providerStatusRow}>
                        <Text style={styles.providerTitle}>
                          {formatProviderLabel(item.provider)} - {getOutcomeLabel(item.last_validation_outcome)}
                        </Text>
                        <Text style={styles.providerHint}>{item.remediation_hint}</Text>
                        {item.key_name ? (
                          <Text style={styles.providerMeta}>Key: {item.key_name}</Text>
                        ) : null}
                        {item.last_validation_at ? (
                          <Text style={styles.providerMeta}>Last validation: {item.last_validation_at}</Text>
                        ) : null}
                        {item.validation_error ? (
                          <Text style={styles.providerError}>Validation error: {item.validation_error}</Text>
                        ) : null}
                      </View>
                    ))}
                  </View>
                  <TouchableOpacity
                    testID="settings-refresh-key-status"
                    style={styles.refreshButton}
                    onPress={loadKeyStatus}
                  >
                    <Text style={styles.refreshButtonText}>Refresh provider status</Text>
                  </TouchableOpacity>
                </>
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Provider Cost Guidance</Text>
            <View style={styles.statusCard}>
              <Text testID="settings-cost-default" style={styles.statusText}>
                Default budget path: Environment mode uses OpenRouter + OpenAI TTS to keep baseline costs lower.
              </Text>
              <Text testID="settings-cost-premium" style={styles.statusSubtle}>
                Premium path: BYOK mode uses your own OpenRouter + ElevenLabs keys for higher-quality voice at provider-defined pricing.
              </Text>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Available Now</Text>
            {settingsItems.map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.settingItem}
                onPress={item.onPress}>
                <Text style={styles.settingIcon}>{item.icon}</Text>
                <View style={styles.settingContent}>
                  <Text style={styles.settingTitle}>{item.title}</Text>
                  <Text style={styles.settingDescription}>{item.description}</Text>
                </View>
                <Text style={styles.arrow}>›</Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Roadmap Modules</Text>
            {comingSoonItems.map((item, index) => (
              <View key={index} style={[styles.settingItem, styles.disabledItem]}>
                <Text style={styles.settingIcon}>{item.icon}</Text>
                <View style={styles.settingContent}>
                  <Text style={[styles.settingTitle, styles.disabledText]}>
                    {item.title}
                  </Text>
                  <Text style={[styles.settingDescription, styles.disabledText]}>
                    {item.description}
                  </Text>
                </View>
                <Text style={[styles.arrow, styles.disabledText]}>⏳</Text>
              </View>
            ))}
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              LearnOnTheGo v1.0.0
            </Text>
            <Text style={styles.footerSubtext}>
              Built for focused, cost-conscious AI learning systems
            </Text>
          </View>
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
    left: -60,
    width: 240,
    height: 240,
    backgroundColor: 'rgba(198, 168, 106, 0.08)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -40,
    right: -120,
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
    fontSize: 44,
    lineHeight: 48,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 10,
  },
  pageSubtitle: {
    color: '#aeb6c7',
    fontSize: 15,
    lineHeight: 22,
  },
  panel: {
    flex: 1.1,
    backgroundColor: '#f2f0ea',
    padding: 18,
  },
  section: {
    marginBottom: 18,
  },
  statusCard: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    padding: 14,
  },
  statusText: {
    color: '#243045',
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '600',
  },
  statusSubtle: {
    color: '#59667b',
    fontSize: 13,
    lineHeight: 18,
    marginTop: 6,
  },
  providerStatusList: {
    marginTop: 10,
    gap: 8,
  },
  providerStatusRow: {
    borderWidth: 1,
    borderColor: '#d4d8e1',
    backgroundColor: '#ffffff',
    padding: 10,
  },
  providerTitle: {
    color: '#1f2a3d',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 4,
  },
  providerHint: {
    color: '#4c5a73',
    fontSize: 12,
    lineHeight: 17,
  },
  providerMeta: {
    color: '#5f6a7f',
    fontSize: 11,
    marginTop: 4,
  },
  providerError: {
    color: '#8b2f2f',
    fontSize: 11,
    marginTop: 4,
  },
  refreshButton: {
    marginTop: 12,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#30384a',
    backgroundColor: '#fdf8ec',
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  refreshButtonText: {
    color: '#30384a',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 12,
  },
  settingItem: {
    backgroundColor: '#f8f7f3',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#b7bcc8',
  },
  disabledItem: {
    opacity: 0.6,
  },
  settingIcon: {
    fontSize: 24,
    marginRight: 16,
    width: 32,
    textAlign: 'center',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1e2431',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#5a6272',
  },
  disabledText: {
    color: '#8d95a4',
  },
  arrow: {
    fontSize: 20,
    color: '#4f5768',
    marginLeft: 8,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#c9ccd4',
    paddingTop: 12,
  },
  footerText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#3f4758',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#636a78',
    lineHeight: 18,
  },
});

export default SettingsScreen;
