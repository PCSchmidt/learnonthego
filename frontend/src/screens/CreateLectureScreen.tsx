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
  LecturePlayer: { lectureId: string };
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

  const getUrlOutcomeGuidance = (diagnostics: UrlDiagnosticsResponse): string => {
    switch (diagnostics.outcome) {
      case 'unreachable':
        return 'The service could not reach this URL. Verify the link and try diagnostics again.';
      case 'unsupported':
        return 'This URL type is recognized but not supported for generation in this slice.';
      case 'no_transcript':
        return 'Transcript extraction is required first. Video transcript ingestion is not yet enabled.';
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

    setIsLoading(true);

    try {
      const response = await lectureService.createLecture(lectureRequest, {
        useByok,
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
                navigation.navigate('LecturePlayer', { lectureId: generatedLectureId });
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
              { id: 'url', label: 'URL (Next)' },
            ].map(option => (
              <TouchableOpacity
                key={option.id}
                testID={`source-mode-${option.id}`}
                style={[
                  styles.sourceSwitchButton,
                  sourceMode === option.id && styles.sourceSwitchButtonActive,
                ]}
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
              Run URL diagnostics first. URL generation is allowed only when diagnostics outcome is ready.
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
              <TouchableOpacity testID="pick-file-button" style={styles.filePickButton} onPress={pickFileForSource}>
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
                <TouchableOpacity testID="clear-file-button" onPress={resetFileSelection} style={styles.fileResetButton}>
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
                onPress={() => navigation.navigate('Settings')}
              >
                <Text style={styles.modeTooltipLinkText}>
                  Tip: Compare provider pricing in Settings -> Provider Cost Guidance.
                </Text>
              </TouchableOpacity>
              <View style={styles.modeActions}>
                <TouchableOpacity
                  testID="generation-mode-byok"
                  style={[styles.modeButton, useByok && styles.modeButtonActive]}
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
            <Text style={styles.modeSubtle}>
              Confirm to generate audio, or change inputs to regenerate preview.
            </Text>
          </View>
        ) : null}

        <TouchableOpacity
          testID="create-lecture-button"
          style={[styles.createButton, isLoading && styles.createButtonDisabled]}
          onPress={handleCreateLecture}
          disabled={isLoading || (sourceMode === 'url' && (!isUrlGenerationEnabled || urlDiagnostics?.outcome !== 'ready'))}>
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator color="#ffffff" />
              <Text style={styles.loadingText}>Generating your lecture...</Text>
            </View>
          ) : (
            <Text style={styles.createButtonText}>
              {sourceMode === 'url' && !isUrlGenerationEnabled
                ? 'URL Generation Disabled By Feature Flag'
                : sourceMode === 'url' && urlDiagnostics?.outcome !== 'ready'
                  ? 'Run Diagnostics Until URL Is Ready'
                  : scriptPreview?.dry_run
                    ? 'Confirm And Generate Audio'
                  : sourceMode === 'url'
                    ? 'Preview Script From URL'
                    : 'Preview Script'}
            </Text>
          )}
        </TouchableOpacity>
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
    left: -70,
    width: 260,
    height: 260,
    backgroundColor: 'rgba(198, 168, 106, 0.08)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: 90,
    right: -100,
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
    fontSize: 46,
    lineHeight: 50,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 10,
  },
  pageSubtitle: {
    color: '#aeb6c7',
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 22,
  },
  metaBlock: {
    borderTopWidth: 1,
    borderTopColor: '#2a3140',
    paddingTop: 12,
  },
  metaLabel: {
    color: '#7e8798',
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
    marginBottom: 6,
  },
  metaValue: {
    color: '#d6dbe6',
    fontSize: 14,
    fontWeight: '600',
  },
  formPanel: {
    flex: 1.1,
    backgroundColor: '#f2f0ea',
    padding: 20,
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: 8,
    marginTop: 16,
  },
  textInput: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    padding: 16,
    fontSize: 16,
    color: '#0d1119',
    textAlignVertical: 'top',
    minHeight: 80,
  },
  sourceSwitchRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  sourceSwitchButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#b7bcc8',
    backgroundColor: '#f8f7f3',
    paddingVertical: 11,
    alignItems: 'center',
  },
  sourceSwitchButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  sourceSwitchButtonText: {
    color: '#2f3644',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.6,
    textTransform: 'uppercase',
  },
  sourceSwitchButtonTextActive: {
    color: '#f2efe8',
  },
  sourceHelperText: {
    marginTop: 8,
    color: '#5a6272',
    fontSize: 12,
    lineHeight: 16,
  },
  fileCard: {
    marginTop: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#b7bcc8',
    backgroundColor: '#f8f7f3',
  },
  fileLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 4,
  },
  fileSubtle: {
    color: '#616979',
    fontSize: 12,
    marginBottom: 10,
  },
  filePickButton: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#111722',
    paddingVertical: 8,
    paddingHorizontal: 14,
    backgroundColor: '#111722',
  },
  filePickButtonText: {
    color: '#f2efe8',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  fileMeta: {
    marginTop: 8,
    color: '#2f3644',
    fontSize: 12,
  },
  fileResetButton: {
    marginTop: 8,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#939aa8',
    paddingVertical: 6,
    paddingHorizontal: 10,
    backgroundColor: '#ffffff',
  },
  fileResetButtonText: {
    color: '#2f3644',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  urlCard: {
    marginTop: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#b7bcc8',
    backgroundColor: '#f8f7f3',
  },
  urlLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 8,
  },
  urlInput: {
    borderWidth: 1,
    borderColor: '#b7bcc8',
    backgroundColor: '#ffffff',
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: '#111722',
    fontSize: 14,
  },
  urlDiagnosticsButton: {
    marginTop: 10,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#111722',
    backgroundColor: '#111722',
    paddingVertical: 8,
    paddingHorizontal: 14,
  },
  urlDiagnosticsButtonText: {
    color: '#f2efe8',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  fieldError: {
    color: '#a93d2a',
    fontSize: 12,
    marginTop: 6,
    fontWeight: '600',
  },
  formError: {
    marginTop: 12,
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
    fontSize: 12,
    color: '#616979',
    textAlign: 'right',
    marginTop: 4,
  },
  durationScroll: {
    marginTop: 8,
  },
  durationButton: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 60,
    alignItems: 'center',
  },
  durationButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  durationButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2f3644',
  },
  durationButtonTextActive: {
    color: '#f2efe8',
  },
  difficultyContainer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  difficultyButton: {
    flex: 1,
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    alignItems: 'center',
  },
  difficultyButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  difficultyButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2f3644',
  },
  difficultyButtonTextActive: {
    color: '#f2efe8',
  },
  infoCard: {
    backgroundColor: '#ece9df',
    padding: 16,
    borderWidth: 1,
    borderColor: '#c3b188',
    marginTop: 20,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#3e3525',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  infoText: {
    fontSize: 14,
    color: '#4f4635',
    lineHeight: 20,
  },
  createButton: {
    backgroundColor: '#d7bf89',
    borderWidth: 1,
    borderColor: '#a9905d',
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  createButtonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    color: '#11151e',
    fontSize: 14,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  modeCard: {
    marginTop: 16,
    padding: 14,
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
  },
  modeTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2b3240',
    letterSpacing: 0.8,
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
    borderColor: '#b7bcc8',
    backgroundColor: '#f1efe7',
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  modeTooltipLinkText: {
    color: '#2f3644',
    fontSize: 12,
    fontWeight: '600',
  },
  modeActions: {
    flexDirection: 'row',
    gap: 8,
  },
  modeButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#939aa8',
    paddingVertical: 10,
    alignItems: 'center',
  },
  modeButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  modeButtonText: {
    color: '#2f3644',
    fontWeight: '600',
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  modeButtonTextActive: {
    color: '#f2efe8',
  },
  // Voice Selection Styles
  voiceScroll: {
    marginTop: 8,
  },
  voiceButton: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
    minWidth: 140,
    alignItems: 'center',
  },
  voiceButtonActive: {
    backgroundColor: '#111722',
    borderColor: '#111722',
  },
  voiceButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2f3644',
    textAlign: 'center',
  },
  voiceButtonTextActive: {
    color: '#f2efe8',
  },
  // Loading Styles
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  loadingText: {
    color: '#11151e',
    fontSize: 14,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
});

export default CreateLectureScreen;
