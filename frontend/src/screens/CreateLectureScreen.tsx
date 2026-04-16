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
import { UrlIngestionPreviewStep } from '../components';
import { colors, spacing, typography } from '../theme/tokens';
import PremiumButton from '../components/ui/PremiumButton';
import lectureService, {
  ApiKeyStatus,
  AVAILABLE_VOICES,
  DIFFICULTY_LEVELS,
  LectureResponse,
  LectureRequest,
  MODEL_PRESETS,
  ModelPresetId,
  SourceIntakeErrorDetail,
  SourceInputType,
  UrlDiagnosticsResponse,
} from '../services/lecture';
import { StackNavigationProp } from '@react-navigation/stack';

// Navigation types
type RootStackParamList = {
  Home: undefined;
  CreateLecture: undefined;
  LecturePlayer: {
    lectureId: string;
    audioUrl?: string | null;
    title?: string;
    script?: string;
    duration?: number;
    difficulty?: string;
    citations?: Array<{ label?: string; source_uri?: string; note?: string }>;
    sourceContext?: {
      source_uri?: string | null;
      source_class?: string;
      retrieval_method?: string;
      retrieval_timestamp?: string;
      excerpt?: string;
      source_name?: string;
    };
  };
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
  const [sourceMode, setSourceMode] = useState<'text' | 'file' | 'url'>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState('');
  const [isUrlDiagnosticsLoading, setIsUrlDiagnosticsLoading] = useState(false);
  const [urlDiagnostics, setUrlDiagnostics] = useState<UrlDiagnosticsResponse | null>(null);
  const [modelPreset, setModelPreset] = useState<ModelPresetId>('balanced');
  const [isAdvancedModelMode, setIsAdvancedModelMode] = useState(false);
  const [customModelId, setCustomModelId] = useState('');
  const [scriptPreview, setScriptPreview] = useState<LectureResponse | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{
    source?: string;
    topic?: string;
    file?: string;
    url?: string;
    model?: string;
    general?: string;
  }>({});
  const [formData, setFormData] = useState<LectureRequest>({
    topic: '',
    duration: 15,
    difficulty: 'beginner',
    voice: 'Rachel', // Default to first available voice
  });
  const isUrlGenerationEnabled = process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1 === 'true';

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

  const clearFieldError = (field: 'source' | 'topic' | 'file' | 'url' | 'model' | 'general') => {
    setFieldErrors(prev => ({ ...prev, [field]: undefined }));
  };

  const clearPreview = () => {
    setScriptPreview(null);
  };

  const missingByokKeys = keyStatus?.missing_keys || [];
  const hasMissingByokKeys = missingByokKeys.length > 0;

  const getUrlOutcomeGuidance = (diagnostics: UrlDiagnosticsResponse): string => {
    switch (diagnostics.outcome) {
      case 'unreachable':
        return 'The service could not reach this URL. Verify the link and try diagnostics again.';
      case 'unsupported':
        return 'This URL format is not supported yet. Use article URLs, YouTube links with public captions, or podcast RSS/feed URLs.';
      case 'no_transcript':
        return 'Transcript extraction is required first. For YouTube, ensure captions are available; for podcasts, provide an RSS/feed URL with transcript metadata.';
      case 'ready':
        return isUrlGenerationEnabled
          ? 'URL is ready. You can now generate a lecture from this source.'
          : 'URL looks reachable and classifiable. Generation remains disabled until the URL ingestion feature flag is enabled.';
      default:
        return diagnostics.diagnostics.message;
    }
  };

  const getSourceTypeForUpload = (file: File): SourceInputType | null => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (extension === 'txt') return 'txt';
    if (extension === 'md') return 'md';
    if (extension === 'pdf') return 'pdf';
    return null;
  };

  const pickFileForSource = () => {
    if (Platform.OS !== 'web') {
      Alert.alert(
        'File Upload On Mobile',
        'File picker wiring for mobile is next. For now, use web for .txt/.md/.pdf uploads or switch to pasted text.'
      );
      return;
    }

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.md,.pdf,text/plain,text/markdown,application/pdf';
    input.onchange = () => {
      const chosen = input.files?.[0] || null;
      setSelectedFile(chosen);
      clearPreview();
      if (chosen) {
        clearFieldError('file');
        clearFieldError('source');
      }
    };
    input.click();
  };

  const resetFileSelection = () => {
    setSelectedFile(null);
    clearPreview();
    clearFieldError('file');
    clearFieldError('general');
  };

  const handleRunUrlDiagnostics = async () => {
    clearFieldError('url');
    clearFieldError('general');
    setUrlDiagnostics(null);

    if (!urlInput.trim()) {
      setFieldErrors(prev => ({ ...prev, url: 'Enter a URL before running diagnostics.' }));
      return;
    }

    setIsUrlDiagnosticsLoading(true);
    try {
      const response = await lectureService.diagnoseSourceUrl(urlInput);
      if (response.success && response.data) {
        setUrlDiagnostics(response.data);
      } else {
        setFieldErrors(prev => ({
          ...prev,
          url: response.error || 'URL diagnostics failed. Try again.',
        }));
      }
    } catch (error) {
      setFieldErrors(prev => ({
        ...prev,
        url: error instanceof Error ? error.message : 'URL diagnostics failed. Try again.',
      }));
    } finally {
      setIsUrlDiagnosticsLoading(false);
    }
  };

  const setDeterministicErrorFromDetail = (detail: SourceIntakeErrorDetail | undefined, fallback: string) => {
    if (!detail || detail.schema !== 'source-intake-error-v1') {
      setFieldErrors({ general: fallback || 'Generation failed. Please try again.' });
      return;
    }

    const message = detail.message || fallback || 'Generation failed.';
    switch (detail.code) {
      case 'unsupported_source_type':
      case 'source_type_input_mismatch':
        setFieldErrors({ source: message });
        return;
      case 'invalid_source_input_combination':
        if (sourceMode === 'text') {
          setFieldErrors({ topic: message });
        } else {
          setFieldErrors({ source: message });
        }
        return;
      case 'unsupported_file_extension':
      case 'file_too_large':
      case 'invalid_text_encoding':
      case 'empty_text_content':
      case 'pdf_parse_failed':
        setFieldErrors({ file: message });
        return;
      default:
        setFieldErrors({ general: message });
    }
  };

  const handleCreateLecture = async () => {
    setFieldErrors({});

    if (isAdvancedModelMode && !customModelId.trim()) {
      setFieldErrors({ model: 'Enter a model ID or turn off advanced mode to use a preset.' });
      return;
    }

    if (sourceMode === 'url') {
      if (!isUrlGenerationEnabled) {
        setFieldErrors({
          general: 'URL generation is disabled in this environment. Set EXPO_PUBLIC_ENABLE_URL_INGESTION_V1=true.',
        });
        return;
      }
      if (!urlDiagnostics) {
        setFieldErrors({
          url: 'Run URL diagnostics before generating from URL.',
        });
        return;
      }
      if (urlDiagnostics.outcome !== 'ready') {
        setFieldErrors({
          url: urlDiagnostics.diagnostics.message,
        });
        return;
      }
    }

    if (sourceMode === 'text') {
      if (!formData.topic.trim()) {
        setFieldErrors({ topic: 'Please enter text content for your lecture.' });
        return;
      }

      if (formData.topic.length < 3) {
        setFieldErrors({ topic: 'Topic must be at least 3 characters long.' });
        return;
      }
    }

    if (sourceMode === 'file' && !selectedFile) {
      setFieldErrors({ file: 'Select one file (.txt, .md, or .pdf) to continue.' });
      return;
    }

    const inferredSourceType = selectedFile ? getSourceTypeForUpload(selectedFile) : 'text';
    if (sourceMode === 'file' && !inferredSourceType) {
      setFieldErrors({ file: 'Unsupported file type. Allowed: .txt, .md, .pdf.' });
      return;
    }

    const lectureRequest: LectureRequest = {
      ...formData,
      llmModelPreset: modelPreset,
      llmModelId: isAdvancedModelMode ? customModelId.trim() : undefined,
    };

    const requestingPreview = !scriptPreview;

    if (!requestingPreview && useByok && hasMissingByokKeys) {
      setFieldErrors({
        general: `BYOK confirm is blocked until required keys are configured: ${missingByokKeys.join(', ')}. You can still run preview while you complete key setup in Settings.`,
      });
      return;
    }

    // Keep preview available even if BYOK is selected but keys are missing.
    // In that case, preview runs on the environment path and paid confirm stays blocked.
    const requestUseByok = useByok && !(requestingPreview && hasMissingByokKeys);

    setIsLoading(true);

    try {
      const response = await lectureService.createLecture(lectureRequest, {
        useByok: requestUseByok,
        dryRun: requestingPreview,
        sourceType: (sourceMode === 'file' ? inferredSourceType : sourceMode === 'url' ? 'url' : 'text') as SourceInputType,
        uploadFile: sourceMode === 'file' ? selectedFile || undefined : undefined,
        sourceUrl: sourceMode === 'url' ? urlInput.trim() : undefined,
      });
      
      if (response.success && response.data) {
        if (requestingPreview) {
          if (response.data.dry_run) {
            setScriptPreview(response.data);
            return;
          }
          setFieldErrors({ general: 'Preview response did not match dry-run contract. Please retry.' });
          return;
        }

        const generatedLectureId = response.data.id || `v2-${Date.now()}`;
        const executionMode = response.data.execution_mode || (
          response.data.key_source === 'user-encrypted-storage' ? 'byok' : 'environment'
        );
        const keySource = executionMode === 'byok'
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
                navigation.navigate('LecturePlayer', {
                  lectureId: generatedLectureId,
                  audioUrl: response.data?.audio_url,
                  title: response.data?.title,
                  script: response.data?.script,
                  citations: response.data?.citations,
                  sourceContext: response.data?.source_metadata || response.data?.metadata?.source_context,
                  duration: formData.duration,
                  difficulty: formData.difficulty,
                });
              },
            },
            {
              text: 'View Library',
              onPress: () => navigation.navigate('Home'),
            },
          ]
        );
      } else {
        setDeterministicErrorFromDetail(
          response.errorDetails as SourceIntakeErrorDetail | undefined,
          response.error ||
            (useByok
              ? 'Failed to create lecture using BYOK path. Verify your provider keys in settings.'
              : requestingPreview
                ? 'Failed to generate script preview'
                : 'Failed to create lecture')
        );
      }
    } catch (error) {
      console.error('Error creating lecture:', error);
      setFieldErrors({
        general:
          error instanceof Error
            ? error.message
            : 'Failed to create lecture. Please check your connection and try again.',
      });
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
          <Text style={styles.label}>Source Type</Text>
          <View style={styles.sourceSwitchRow}>
            {[
              { id: 'text', label: 'Text' },
              { id: 'file', label: 'File' },
              { id: 'url', label: 'URL' },
            ].map(option => (
              <TouchableOpacity
                key={option.id}
                testID={`source-mode-${option.id}`}
                style={[
                  styles.sourceSwitchButton,
                  sourceMode === option.id && styles.sourceSwitchButtonActive,
                ]}
                accessibilityRole="button"
                accessibilityLabel={`Source mode ${option.label}`}
                accessibilityHint={`Switches source mode to ${option.label.toLowerCase()}`}
                accessibilityState={{ selected: sourceMode === option.id }}
                onPress={() => {
                  setSourceMode(option.id as 'text' | 'file' | 'url');
                  clearFieldError('source');
                  clearFieldError('topic');
                  clearFieldError('file');
                  clearFieldError('url');
                  clearFieldError('model');
                  clearFieldError('general');
                  clearPreview();
                  if (option.id !== 'url') {
                    setUrlDiagnostics(null);
                  }
                }}>
                <Text
                  style={[
                    styles.sourceSwitchButtonText,
                    sourceMode === option.id && styles.sourceSwitchButtonTextActive,
                  ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          {sourceMode === 'text' ? (
            <Text style={styles.sourceHelperText}>
              Paste your content directly. Best for quick drafts and copied notes.
            </Text>
          ) : null}
          {sourceMode === 'file' ? (
            <Text style={styles.sourceHelperText}>
              Upload one file at a time. Supported: .txt, .md, .pdf.
            </Text>
          ) : null}
          {sourceMode === 'url' ? (
            <Text style={styles.sourceHelperText}>
              Run URL diagnostics first. Supported sources include web pages, YouTube URLs with captions, and podcast RSS/feed URLs with transcript metadata.
            </Text>
          ) : null}
          {fieldErrors.source ? <Text testID="source-error" style={styles.fieldError}>{fieldErrors.source}</Text> : null}

          {sourceMode === 'text' ? (
            <>
          <Text style={styles.label}>Lecture Topic *</Text>
        <TextInput
          testID="topic-input"
          style={styles.textInput}
          value={formData.topic}
          onChangeText={(text) => {
            setFormData({...formData, topic: text});
            clearFieldError('topic');
            clearFieldError('general');
            clearPreview();
          }}
          accessibilityLabel="Lecture topic"
          accessibilityHint="Describe the lecture topic or paste text content"
          placeholder="e.g., Machine Learning Basics, Quantum Physics, History of Rome"
          placeholderTextColor="#7f8492"
          multiline
          numberOfLines={3}
          maxLength={500}
        />
        {fieldErrors.topic ? <Text testID="topic-error" style={styles.fieldError}>{fieldErrors.topic}</Text> : null}
        <Text style={styles.charCount}>{formData.topic.length}/500</Text>
            </>
          ) : null}

          {sourceMode === 'file' ? (
            <View style={styles.fileCard}>
              <Text style={styles.fileLabel}>Upload Source File</Text>
              <Text style={styles.fileSubtle}>Accepted formats: .txt, .md, .pdf</Text>
              <TouchableOpacity
                testID="pick-file-button"
                style={styles.filePickButton}
                onPress={pickFileForSource}
                accessibilityRole="button"
                accessibilityLabel={selectedFile ? 'Change source file' : 'Choose source file'}
                accessibilityHint="Opens file picker for txt, markdown, or PDF sources"
              >
                <Text style={styles.filePickButtonText}>
                  {selectedFile ? 'Change File' : 'Choose File'}
                </Text>
              </TouchableOpacity>
              <Text style={styles.fileMeta}>
                {selectedFile
                  ? `${selectedFile.name} (${Math.max(1, Math.round(selectedFile.size / 1024))} KB)`
                  : 'No file selected'}
              </Text>
              {selectedFile ? (
                <TouchableOpacity
                  testID="clear-file-button"
                  onPress={resetFileSelection}
                  style={styles.fileResetButton}
                  accessibilityRole="button"
                  accessibilityLabel="Clear selected file"
                  accessibilityHint="Removes the currently selected file from this lecture"
                >
                  <Text style={styles.fileResetButtonText}>Clear Selected File</Text>
                </TouchableOpacity>
              ) : null}
              {fieldErrors.file ? <Text testID="file-error" style={styles.fieldError}>{fieldErrors.file}</Text> : null}
            </View>
          ) : null}

          {sourceMode === 'url' ? (
            <UrlIngestionPreviewStep
              urlInput={urlInput}
              onUrlChange={(text) => {
                setUrlInput(text);
                clearFieldError('url');
                clearFieldError('general');
                clearPreview();
              }}
              onRunDiagnostics={handleRunUrlDiagnostics}
              isDiagnosticsLoading={isUrlDiagnosticsLoading}
              diagnostics={urlDiagnostics}
              diagnosticsGuidance={urlDiagnostics ? getUrlOutcomeGuidance(urlDiagnostics) : undefined}
              urlError={fieldErrors.url}
            />
          ) : null}

          {fieldErrors.general ? <Text testID="general-error" style={styles.formError}>{fieldErrors.general}</Text> : null}

        <View style={styles.modeCard}>
          <Text style={styles.modeTitle}>Generation Mode</Text>
          {isStatusLoading ? (
            <Text style={styles.modeSubtle}>Checking key status...</Text>
          ) : (
            <>
              <Text testID="byok-status-summary" style={styles.modeSubtle}>
                {keyStatus?.setup_complete
                  ? 'BYOK keys detected for OpenRouter and ElevenLabs.'
                  : `Missing keys: ${(keyStatus?.missing_keys || []).join(', ') || 'unknown'}`}
              </Text>
              <Text testID="fallback-status-message" style={styles.modeSubtle}>
                {useByok
                  ? 'Primary path: BYOK secure storage (OpenRouter + ElevenLabs).'
                  : 'Fallback path active: Environment-managed providers (OpenRouter + OpenAI TTS).'}
              </Text>
              <Text testID="provider-cost-copy" style={styles.modeSubtle}>
                {useByok
                  ? 'Cost profile: premium quality path. BYOK uses your own OpenRouter and ElevenLabs billing.'
                  : 'Cost profile: default budget path. Environment mode uses OpenRouter with OpenAI TTS to reduce baseline cost.'}
              </Text>
              <TouchableOpacity
                testID="provider-cost-guidance-link"
                style={styles.modeTooltipLink}
                accessibilityRole="button"
                accessibilityLabel="Open provider cost guidance"
                accessibilityHint="Navigates to settings with provider pricing guidance"
                onPress={() => navigation.navigate('Settings')}
              >
                <Text style={styles.modeTooltipLinkText}>
                  Tip: Compare provider pricing in Settings and open Provider Cost Guidance.
                </Text>
              </TouchableOpacity>
              <View style={styles.modeActions}>
                <TouchableOpacity
                  testID="generation-mode-byok"
                  style={[styles.modeButton, useByok && styles.modeButtonActive]}
                  accessibilityRole="button"
                  accessibilityLabel="Generation mode BYOK"
                  accessibilityHint="Use your own provider keys for generation"
                  accessibilityState={{ selected: useByok, disabled: !keyStatus?.setup_complete }}
                  onPress={() => {
                    setUseByok(true);
                    clearPreview();
                  }}
                  disabled={!keyStatus?.setup_complete}
                >
                  <Text style={[styles.modeButtonText, useByok && styles.modeButtonTextActive]}>
                    BYOK
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  testID="generation-mode-environment"
                  style={[styles.modeButton, !useByok && styles.modeButtonActive]}
                  accessibilityRole="button"
                  accessibilityLabel="Generation mode environment"
                  accessibilityHint="Use environment-managed providers for generation"
                  accessibilityState={{ selected: !useByok }}
                  onPress={() => {
                    setUseByok(false);
                    clearPreview();
                  }}
                >
                  <Text style={[styles.modeButtonText, !useByok && styles.modeButtonTextActive]}>
                    Environment
                  </Text>
                </TouchableOpacity>
              </View>
              {!keyStatus?.setup_complete ? (
                <Text testID="byok-settings-hint" style={styles.modeSubtle}>
                  BYOK is unavailable until required keys are configured in Settings.
                </Text>
              ) : null}
            </>
          )}
        </View>

        <View style={styles.modeCard}>
          <Text style={styles.modeTitle}>Model Selection</Text>
          <Text style={styles.modeSubtle}>Pick a preset or provide a raw model ID in advanced mode.</Text>
          <View style={styles.modeActions}>
            {MODEL_PRESETS.map((preset) => (
              <TouchableOpacity
                key={preset.id}
                testID={`model-preset-${preset.id}`}
                style={[styles.modeButton, modelPreset === preset.id && styles.modeButtonActive]}
                accessibilityRole="button"
                accessibilityLabel={`Model preset ${preset.label}`}
                accessibilityState={{ selected: modelPreset === preset.id }}
                onPress={() => {
                  setModelPreset(preset.id);
                  clearFieldError('model');
                  clearPreview();
                }}
              >
                <Text style={[styles.modeButtonText, modelPreset === preset.id && styles.modeButtonTextActive]}>
                  {preset.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={styles.modeSubtle}>
            {MODEL_PRESETS.find((preset) => preset.id === modelPreset)?.description}
          </Text>

          <TouchableOpacity
            testID="model-advanced-toggle"
            style={[styles.modeButton, isAdvancedModelMode && styles.modeButtonActive, { marginTop: 10 }]}
            accessibilityRole="button"
            accessibilityLabel="Advanced model mode"
            accessibilityHint="Toggle custom raw model ID input"
            accessibilityState={{ selected: isAdvancedModelMode }}
            onPress={() => {
              setIsAdvancedModelMode((prev) => !prev);
              clearFieldError('model');
              clearPreview();
            }}
          >
            <Text style={[styles.modeButtonText, isAdvancedModelMode && styles.modeButtonTextActive]}>
              {isAdvancedModelMode ? 'Advanced Model: ON' : 'Advanced Model: OFF'}
            </Text>
          </TouchableOpacity>

          {isAdvancedModelMode ? (
            <TextInput
              testID="model-id-input"
              style={[styles.textInput, { minHeight: 48, marginTop: 10 }]}
              value={customModelId}
              onChangeText={(value) => {
                setCustomModelId(value);
                clearFieldError('model');
                clearPreview();
              }}
              accessibilityLabel="Custom model ID"
              accessibilityHint="Enter a raw provider model ID"
              placeholder="e.g., anthropic/claude-3.5-sonnet"
              placeholderTextColor="#7f8492"
              autoCapitalize="none"
              autoCorrect={false}
            />
          ) : null}
          {fieldErrors.model ? <Text testID="model-error" style={styles.fieldError}>{fieldErrors.model}</Text> : null}
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
              onPress={() => {
                setFormData({...formData, duration});
                clearPreview();
              }}>
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
              onPress={() => {
                setFormData({...formData, difficulty: diff.id as any});
                clearPreview();
              }}>
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
              onPress={() => {
                setFormData({...formData, voice: voice.id});
                clearPreview();
              }}>
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

        {scriptPreview?.dry_run ? (
          <View testID="script-preview-card" style={styles.infoCard}>
            <Text style={styles.infoTitle}>Script Preview</Text>
            <Text testID="script-preview-text" style={styles.infoText}>
              {scriptPreview.preview_script?.content || scriptPreview.script || 'No preview script returned.'}
            </Text>
            {scriptPreview.citations && scriptPreview.citations.length > 0 ? (
              <View testID="script-preview-citations" style={{ marginTop: 10 }}>
                <Text style={styles.infoTitle}>Sources</Text>
                {scriptPreview.citations.map((citation, index) => (
                  <Text key={`${citation.source_uri || 'citation'}-${index}`} style={styles.modeSubtle}>
                    - {citation.source_uri || citation.label || 'source-uri-unavailable'}
                  </Text>
                ))}
              </View>
            ) : null}
            <Text testID="confirm-mode-cost-indicator" style={styles.modeSubtle}>
              {useByok && !hasMissingByokKeys
                ? 'Confirm mode: BYOK (OpenRouter + ElevenLabs). Cost profile: premium path on your provider billing.'
                : 'Confirm mode: Environment (OpenRouter + OpenAI TTS). Cost profile: default budget path.'}
            </Text>
            {useByok && hasMissingByokKeys ? (
              <Text testID="confirm-byok-blocked-hint" style={styles.fieldError}>
                BYOK confirm is blocked until keys are configured: {missingByokKeys.join(', ')}.
              </Text>
            ) : null}
            <Text style={styles.modeSubtle}>
              Confirm to generate audio, or change inputs to regenerate preview.
            </Text>
          </View>
        ) : null}

        <PremiumButton
          testID="create-lecture-button"
          title={
            isLoading
              ? 'Generating your lecture...'
              : sourceMode === 'url' && !isUrlGenerationEnabled
                ? 'URL Generation Disabled By Feature Flag'
                : sourceMode === 'url' && urlDiagnostics?.outcome !== 'ready'
                  ? 'Run Diagnostics Until URL Is Ready'
                  : scriptPreview?.dry_run
                    ? 'Confirm And Generate Audio'
                    : sourceMode === 'url'
                      ? 'Preview Script From URL'
                      : 'Preview Script'
          }
          onPress={handleCreateLecture}
          disabled={isLoading || (sourceMode === 'url' && (!isUrlGenerationEnabled || urlDiagnostics?.outcome !== 'ready'))}
          loading={isLoading}
          accessibilityLabel={scriptPreview?.dry_run ? 'Confirm and generate audio' : 'Preview script'}
          style={{ marginTop: spacing.xl }}
        />
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
    left: -70,
    width: 260,
    height: 260,
    backgroundColor: colors.effect.glowA,
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: 90,
    right: -100,
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
    fontSize: typography.size.display,
    lineHeight: typography.lineHeight.display,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: 10,
  },
  pageSubtitle: {
    color: colors.text.secondaryDark,
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 22,
  },
  metaBlock: {
    borderTopWidth: 1,
    borderTopColor: colors.border.medium,
    paddingTop: spacing.sm,
  },
  metaLabel: {
    color: colors.text.muted,
    fontSize: typography.size.caption,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
    marginBottom: 6,
  },
  metaValue: {
    color: colors.text.secondaryDark,
    fontSize: typography.size.body,
    fontWeight: '600',
  },
  formPanel: {
    flex: 1.1,
    backgroundColor: colors.bg.panel,
    padding: spacing.lg,
  },
  label: {
    fontSize: typography.size.label,
    fontWeight: '700',
    color: colors.border.medium,
    letterSpacing: typography.letterSpacing.normal,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
    marginTop: spacing.md,
  },
  textInput: {
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    padding: spacing.md,
    fontSize: typography.size.bodyLg,
    color: '#0d1119',
    textAlignVertical: 'top',
    minHeight: 80,
  },
  sourceSwitchRow: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  sourceSwitchButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: colors.bg.cardLight,
    paddingVertical: 11,
    alignItems: 'center',
  },
  sourceSwitchButtonActive: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.bg.cardDark,
  },
  sourceSwitchButtonText: {
    color: '#2f3644',
    fontSize: typography.size.label,
    fontWeight: '700',
    letterSpacing: 0.6,
    textTransform: 'uppercase',
  },
  sourceSwitchButtonTextActive: {
    color: colors.text.primaryDark,
  },
  sourceHelperText: {
    marginTop: spacing.xs,
    color: '#5a6272',
    fontSize: typography.size.label,
    lineHeight: 16,
  },
  fileCard: {
    marginTop: spacing.sm,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: colors.bg.cardLight,
  },
  fileLabel: {
    fontSize: typography.size.label,
    fontWeight: '700',
    color: colors.border.medium,
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
    marginBottom: 4,
  },
  fileSubtle: {
    color: '#616979',
    fontSize: typography.size.label,
    marginBottom: 10,
  },
  filePickButton: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: colors.bg.cardDark,
    paddingVertical: spacing.xs,
    paddingHorizontal: 14,
    backgroundColor: colors.bg.cardDark,
  },
  filePickButtonText: {
    color: colors.text.primaryDark,
    fontSize: typography.size.label,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
  },
  fileMeta: {
    marginTop: spacing.xs,
    color: '#2f3644',
    fontSize: typography.size.label,
  },
  fileResetButton: {
    marginTop: spacing.xs,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#939aa8',
    paddingVertical: 6,
    paddingHorizontal: 10,
    backgroundColor: '#ffffff',
  },
  fileResetButtonText: {
    color: '#2f3644',
    fontSize: typography.size.caption,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  urlCard: {
    marginTop: spacing.sm,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: colors.bg.cardLight,
  },
  urlLabel: {
    fontSize: typography.size.label,
    fontWeight: '700',
    color: colors.border.medium,
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
    marginBottom: spacing.xs,
  },
  urlInput: {
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: '#ffffff',
    paddingHorizontal: spacing.sm,
    paddingVertical: 10,
    color: colors.bg.cardDark,
    fontSize: typography.size.body,
  },
  urlDiagnosticsButton: {
    marginTop: 10,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: colors.bg.cardDark,
    backgroundColor: colors.bg.cardDark,
    paddingVertical: spacing.xs,
    paddingHorizontal: 14,
  },
  urlDiagnosticsButtonText: {
    color: colors.text.primaryDark,
    fontSize: typography.size.label,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  fieldError: {
    color: '#a93d2a',
    fontSize: typography.size.label,
    marginTop: 6,
    fontWeight: '600',
  },
  formError: {
    marginTop: spacing.sm,
    borderWidth: 1,
    borderColor: '#c06b5d',
    backgroundColor: '#f8e7e3',
    padding: 10,
    color: '#7d2f22',
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '600',
  },
  charCount: {
    fontSize: typography.size.label,
    color: '#616979',
    textAlign: 'right',
    marginTop: 4,
  },
  durationScroll: {
    marginTop: spacing.xs,
  },
  durationButton: {
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginRight: spacing.xs,
    minWidth: 60,
    alignItems: 'center',
  },
  durationButtonActive: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.bg.cardDark,
  },
  durationButtonText: {
    fontSize: typography.size.body,
    fontWeight: '600',
    color: '#2f3644',
  },
  durationButtonTextActive: {
    color: colors.text.primaryDark,
  },
  difficultyContainer: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  difficultyButton: {
    flex: 1,
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    paddingVertical: spacing.sm,
    alignItems: 'center',
  },
  difficultyButtonActive: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.bg.cardDark,
  },
  difficultyButtonText: {
    fontSize: typography.size.body,
    fontWeight: '600',
    color: '#2f3644',
  },
  difficultyButtonTextActive: {
    color: colors.text.primaryDark,
  },
  infoCard: {
    backgroundColor: '#ece9df',
    padding: spacing.md,
    borderWidth: 1,
    borderColor: '#c3b188',
    marginTop: spacing.lg,
  },
  infoTitle: {
    fontSize: typography.size.body,
    fontWeight: '700',
    color: '#3e3525',
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
  },
  infoText: {
    fontSize: typography.size.body,
    color: '#4f4635',
    lineHeight: typography.lineHeight.body,
  },
  modeCard: {
    marginTop: spacing.md,
    padding: 14,
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
  },
  modeTitle: {
    fontSize: typography.size.label,
    fontWeight: '700',
    color: colors.border.medium,
    letterSpacing: typography.letterSpacing.normal,
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  modeSubtle: {
    fontSize: 13,
    color: '#616979',
    marginBottom: 10,
  },
  modeTooltipLink: {
    marginTop: -2,
    marginBottom: 10,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: '#f1efe7',
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  modeTooltipLinkText: {
    color: '#2f3644',
    fontSize: typography.size.label,
    fontWeight: '600',
  },
  modeActions: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  modeButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#939aa8',
    paddingVertical: 10,
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.bg.cardDark,
  },
  modeButtonText: {
    color: '#2f3644',
    fontWeight: '600',
    fontSize: typography.size.label,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  modeButtonTextActive: {
    color: colors.text.primaryDark,
  },
  voiceScroll: {
    marginTop: spacing.xs,
  },
  voiceButton: {
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginRight: spacing.xs,
    minWidth: 140,
    alignItems: 'center',
  },
  voiceButtonActive: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.bg.cardDark,
  },
  voiceButtonText: {
    fontSize: typography.size.label,
    fontWeight: '600',
    color: '#2f3644',
    textAlign: 'center',
  },
  voiceButtonTextActive: {
    color: colors.text.primaryDark,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  loadingText: {
    color: colors.accent.brassText,
    fontSize: typography.size.body,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
  },
});

export default CreateLectureScreen;
