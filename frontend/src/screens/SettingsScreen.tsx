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
import { colors, spacing, typography } from '../theme/tokens';
import PremiumButton from '../components/ui/PremiumButton';
import PremiumField from '../components/ui/PremiumField';
import PremiumPanel from '../components/ui/PremiumPanel';

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
  const [isSavingKey, setIsSavingKey] = useState(false);
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [openRouterKey, setOpenRouterKey] = useState('');
  const [elevenLabsKey, setElevenLabsKey] = useState('');

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

  const handleSaveKey = async (provider: 'openrouter' | 'elevenlabs') => {
    const rawKey = provider === 'openrouter' ? openRouterKey : elevenLabsKey;
    const normalizedKey = rawKey.trim();
    if (!normalizedKey) {
      Alert.alert('Missing API key', `Enter your ${formatProviderLabel(provider)} API key first.`);
      return;
    }

    setIsSavingKey(true);
    try {
      const storeResponse = await lectureService.storeApiKey(provider, normalizedKey);
      if (!storeResponse.success) {
        Alert.alert('Save failed', storeResponse.error || 'Unable to save API key.');
        return;
      }

      const validateResponse = await lectureService.validateApiKey(provider);
      if (validateResponse.success && validateResponse.data?.is_valid) {
        Alert.alert('Key saved', `${formatProviderLabel(provider)} key saved and validated.`);
      } else {
        Alert.alert(
          'Key saved but not validated',
          validateResponse.data?.message || validateResponse.error || 'Recheck the key and provider account.'
        );
      }

      if (provider === 'openrouter') {
        setOpenRouterKey('');
      } else {
        setElevenLabsKey('');
      }

      await loadKeyStatus();
    } finally {
      setIsSavingKey(false);
    }
  };

  const handleDeleteKey = async (provider: 'openrouter' | 'elevenlabs') => {
    setIsSavingKey(true);
    try {
      const response = await lectureService.deleteApiKey(provider);
      if (!response.success) {
        Alert.alert('Delete failed', response.error || 'Unable to delete API key.');
        return;
      }

      Alert.alert('Key removed', `${formatProviderLabel(provider)} key deleted.`);
      await loadKeyStatus();
    } finally {
      setIsSavingKey(false);
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
                  <PremiumButton
                    testID="settings-refresh-key-status"
                    title="Refresh provider status"
                    variant="secondary"
                    onPress={loadKeyStatus}
                  />
                </>
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>BYOK Key Entry</Text>
            <View style={styles.statusCard}>
              <Text style={styles.statusText}>Add your provider keys for BYOK generation.</Text>
              <Text style={styles.statusSubtle}>
                Keys are encrypted server-side and tied to your signed-in user account.
              </Text>

              <View style={styles.keyFormSection}>
                <PremiumField
                  label="OpenRouter API Key"
                  testID="settings-openrouter-key-input"
                  value={openRouterKey}
                  onChangeText={setOpenRouterKey}
                  placeholder="sk-or-v1-..."
                  autoCapitalize="none"
                  autoCorrect={false}
                  secureTextEntry
                  editable={!isSavingKey}
                />
                <View style={styles.keyButtonRow}>
                  <PremiumButton
                    testID="settings-openrouter-save-validate"
                    title="Save + Validate"
                    onPress={() => handleSaveKey('openrouter')}
                    disabled={isSavingKey}
                    loading={isSavingKey}
                    style={styles.keyButton}
                  />
                  <PremiumButton
                    testID="settings-openrouter-delete"
                    title="Delete"
                    variant="danger"
                    onPress={() => handleDeleteKey('openrouter')}
                    disabled={isSavingKey}
                    style={styles.keyButton}
                  />
                </View>
              </View>

              <View style={styles.keyFormSection}>
                <PremiumField
                  label="ElevenLabs API Key"
                  testID="settings-elevenlabs-key-input"
                  value={elevenLabsKey}
                  onChangeText={setElevenLabsKey}
                  placeholder="sk-..."
                  autoCapitalize="none"
                  autoCorrect={false}
                  secureTextEntry
                  editable={!isSavingKey}
                />
                <View style={styles.keyButtonRow}>
                  <PremiumButton
                    testID="settings-elevenlabs-save-validate"
                    title="Save + Validate"
                    onPress={() => handleSaveKey('elevenlabs')}
                    disabled={isSavingKey}
                    loading={isSavingKey}
                    style={styles.keyButton}
                  />
                  <PremiumButton
                    testID="settings-elevenlabs-delete"
                    title="Delete"
                    variant="danger"
                    onPress={() => handleDeleteKey('elevenlabs')}
                    disabled={isSavingKey}
                    style={styles.keyButton}
                  />
                </View>
              </View>
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
    backgroundColor: colors.bg.canvas,
  },
  contentContainer: {
    padding: 18,
    paddingBottom: spacing.xl,
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -100,
    left: -60,
    width: 240,
    height: 240,
    backgroundColor: colors.effect.glowA,
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -40,
    right: -120,
    width: 290,
    height: 290,
    backgroundColor: colors.effect.glowB,
  },
  shell: {
    width: '100%',
    maxWidth: 1180,
    alignSelf: 'center',
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    borderWidth: 1,
    borderColor: colors.border.dark,
    backgroundColor: '#0b0d12',
  },
  headerRail: {
    flex: 0.9,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
    borderBottomWidth: Platform.OS === 'web' ? 0 : 1,
    borderRightColor: colors.border.dark,
    borderBottomColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xl,
  },
  eyebrow: {
    color: colors.accent.brass,
    fontSize: typography.size.label,
    letterSpacing: typography.letterSpacing.wide,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 10,
  },
  pageTitle: {
    color: colors.text.primaryDark,
    fontSize: 44,
    lineHeight: 48,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: 10,
  },
  pageSubtitle: {
    color: colors.text.secondaryDark,
    fontSize: 15,
    lineHeight: 22,
  },
  panel: {
    flex: 1.1,
    backgroundColor: colors.bg.panel,
    padding: 18,
  },
  section: {
    marginBottom: 18,
  },
  statusCard: {
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    padding: 14,
  },
  statusText: {
    color: '#243045',
    fontSize: typography.size.body,
    lineHeight: typography.lineHeight.body,
    fontWeight: '600',
  },
  statusSubtle: {
    color: colors.text.secondaryLight,
    fontSize: 13,
    lineHeight: 18,
    marginTop: 6,
  },
  providerStatusList: {
    marginTop: 10,
    gap: spacing.xs,
  },
  providerStatusRow: {
    borderWidth: 1,
    borderColor: '#d4d8e1',
    backgroundColor: '#ffffff',
    padding: 10,
  },
  providerTitle: {
    color: colors.text.primaryLight,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 4,
  },
  providerHint: {
    color: colors.text.secondaryLight,
    fontSize: typography.size.label,
    lineHeight: 17,
  },
  providerMeta: {
    color: colors.text.muted,
    fontSize: typography.size.caption,
    marginTop: 4,
  },
  providerError: {
    color: '#8b2f2f',
    fontSize: typography.size.caption,
    marginTop: 4,
  },
  keyFormSection: {
    marginTop: spacing.sm,
    borderWidth: 1,
    borderColor: '#d4d8e1',
    backgroundColor: '#ffffff',
    padding: 10,
  },
  keyButtonRow: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: 10,
  },
  keyButton: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: typography.size.label,
    fontWeight: '700',
    color: colors.border.medium,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: spacing.sm,
  },
  settingItem: {
    backgroundColor: colors.bg.cardLight,
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    marginBottom: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border.light,
  },
  disabledItem: {
    opacity: 0.6,
  },
  settingIcon: {
    fontSize: 24,
    marginRight: spacing.md,
    width: 32,
    textAlign: 'center',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: typography.size.bodyLg,
    fontWeight: '700',
    color: colors.text.primaryLight,
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: typography.size.body,
    color: colors.text.secondaryLight,
  },
  disabledText: {
    color: colors.text.muted,
  },
  arrow: {
    fontSize: 20,
    color: colors.text.secondaryLight,
    marginLeft: spacing.xs,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: colors.border.light,
    paddingTop: spacing.sm,
  },
  footerText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.text.secondaryLight,
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
  },
  footerSubtext: {
    fontSize: typography.size.label,
    color: colors.text.muted,
    lineHeight: 18,
  },
});

export default SettingsScreen;
