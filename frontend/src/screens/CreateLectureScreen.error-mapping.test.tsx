import React from 'react';
import { fireEvent, render, waitFor } from '@testing-library/react-native';
import { Platform } from 'react-native';

import CreateLectureScreen from './CreateLectureScreen';
import lectureService from '../services/lecture';

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
  }),
}));

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'tester@example.com' },
  }),
}));

jest.mock('../services/lecture', () => ({
  __esModule: true,
  default: {
    getApiKeyStatus: jest.fn(),
    createLecture: jest.fn(),
    diagnoseSourceUrl: jest.fn(),
  },
  AVAILABLE_VOICES: [
    { id: 'Rachel', name: 'Rachel (Professional Female)' },
    { id: 'Josh', name: 'Josh (Professional Male)' },
  ],
  DIFFICULTY_LEVELS: [
    { id: 'beginner', name: 'Beginner', description: 'Basic concepts and simple explanations' },
    { id: 'intermediate', name: 'Intermediate', description: 'Moderate complexity with examples' },
    { id: 'advanced', name: 'Advanced', description: 'In-depth analysis and technical details' },
  ],
  MODEL_PRESETS: [
    {
      id: 'cost_saver',
      label: 'Cost Saver',
      model: 'openai/gpt-4.1-mini',
      description: 'Lowest cost with solid quality for general topics.',
    },
    {
      id: 'balanced',
      label: 'Balanced',
      model: 'anthropic/claude-3.5-sonnet',
      description: 'Recommended default for quality and consistency.',
    },
    {
      id: 'high_fidelity',
      label: 'High Fidelity',
      model: 'openai/gpt-4.1',
      description: 'Higher quality reasoning with increased cost.',
    },
  ],
}));

describe('CreateLectureScreen deterministic error mapping', () => {
  const mockAlert = jest.spyOn(require('react-native').Alert, 'alert').mockImplementation(jest.fn());
  const originalUrlFlag = process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1;

  beforeEach(() => {
    jest.clearAllMocks();
    process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1 = 'false';
    Object.defineProperty(Platform, 'OS', {
      configurable: true,
      get: () => 'web',
    });
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        can_generate_lectures: true,
        missing_keys: [],
        setup_complete: true,
      },
    });
    (lectureService.createLecture as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        title: 'Dry Run Lecture Contract',
        script: 'Dry run mode validates contract only. No LLM/TTS generation executed.',
        preview_script: {
          title: 'Dry Run Lecture Contract',
          content: 'Dry run mode validates contract only. No LLM/TTS generation executed.',
          duration_minutes: 15,
          difficulty: 'beginner',
        },
        dry_run: true,
        key_source: 'environment',
      },
    });
    (lectureService.diagnoseSourceUrl as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        success: true,
        schema: 'url-diagnostics-v1',
        contract_version: 'v1a',
        source_uri: 'https://example.com',
        source_class: 'web',
        outcome: 'ready',
        diagnostics: {
          code: 'ready',
          message: 'URL is reachable and ready for upcoming web-source ingestion flow.',
          retryable: false,
          status_code: 200,
        },
      },
    });
  });

  afterAll(() => {
    process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1 = originalUrlFlag;
    mockAlert.mockRestore();
  });

  it('maps unsupported_source_type to source field', async () => {
    (lectureService.createLecture as jest.Mock).mockResolvedValue({
      success: false,
      error: 'bad request',
      errorDetails: {
        schema: 'source-intake-error-v1',
        code: 'unsupported_source_type',
        message: 'Source type is not supported in v1a.',
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    fireEvent.changeText(getByTestId('topic-input'), 'A valid topic for submission');
    fireEvent.press(getByTestId('create-lecture-button'));

    const sourceError = await findByTestId('source-error');
    expect(sourceError.props.children).toBe('Source type is not supported in v1a.');
  });

  it('maps invalid_source_input_combination to topic field when in text mode', async () => {
    (lectureService.createLecture as jest.Mock).mockResolvedValue({
      success: false,
      error: 'bad request',
      errorDetails: {
        schema: 'source-intake-error-v1',
        code: 'invalid_source_input_combination',
        message: 'Provide exactly one input source: either document_text or file.',
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    fireEvent.changeText(getByTestId('topic-input'), 'Another valid topic');
    fireEvent.press(getByTestId('create-lecture-button'));

    const topicError = await findByTestId('topic-error');
    expect(topicError.props.children).toBe('Provide exactly one input source: either document_text or file.');
  });

  it('maps file_too_large to file field when in file mode', async () => {
    (lectureService.createLecture as jest.Mock).mockResolvedValue({
      success: false,
      error: 'bad request',
      errorDetails: {
        schema: 'source-intake-error-v1',
        code: 'file_too_large',
        message: 'Text file size must be under 2MB.',
      },
    });

    const file = { name: 'notes.txt', size: 1024, type: 'text/plain' };

    const documentMock = {
      createElement: jest.fn(() => {
        const input: any = {
          type: 'file',
          accept: '',
          files: [file],
          onchange: null,
          click: function click() {
            if (typeof input.onchange === 'function') {
              input.onchange();
            }
          },
        };
        return input;
      }),
    };

    Object.defineProperty(global, 'document', {
      value: documentMock,
      configurable: true,
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    fireEvent.press(getByTestId('source-mode-file'));
    fireEvent.press(getByTestId('pick-file-button'));
    fireEvent.press(getByTestId('create-lecture-button'));

    const fileError = await findByTestId('file-error');
    expect(fileError.props.children).toBe('Text file size must be under 2MB.');
  });

  it('maps unknown schema to general field', async () => {
    (lectureService.createLecture as jest.Mock).mockResolvedValue({
      success: false,
      error: 'Generic failure fallback',
      errorDetails: {
        schema: 'unexpected-schema',
        code: 'anything',
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    fireEvent.changeText(getByTestId('topic-input'), 'Valid topic text');
    fireEvent.press(getByTestId('create-lecture-button'));

    const generalError = await findByTestId('general-error');
    expect(generalError.props.children).toBe('Generic failure fallback');

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });
  });

  it('submits text mode with sourceType text and no upload file', async () => {
    const { getByTestId } = render(<CreateLectureScreen />);

    fireEvent.changeText(getByTestId('topic-input'), 'Text mode payload verification');
    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });

    const [, options] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    const [request] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    expect(options.sourceType).toBe('text');
    expect(options.uploadFile).toBeUndefined();
    expect(request.llmModelPreset).toBe('balanced');
  });

  it('forwards selected model preset in create request', async () => {
    const { getByTestId } = render(<CreateLectureScreen />);

    fireEvent.press(getByTestId('model-preset-cost_saver'));
    fireEvent.changeText(getByTestId('topic-input'), 'Preset forwarding coverage');
    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });

    const [request] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    expect(request.llmModelPreset).toBe('cost_saver');
    expect(request.llmModelId).toBeUndefined();
  });

  it('forwards advanced raw model in create request', async () => {
    const { getByTestId } = render(<CreateLectureScreen />);

    fireEvent.press(getByTestId('model-advanced-toggle'));
    fireEvent.changeText(getByTestId('model-id-input'), 'openai/gpt-4.1');
    fireEvent.changeText(getByTestId('topic-input'), 'Advanced model forwarding coverage');
    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });

    const [request] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    expect(request.llmModelPreset).toBe('balanced');
    expect(request.llmModelId).toBe('openai/gpt-4.1');
  });

  it('shows fallback messaging when BYOK is not configured and environment mode is selected', async () => {
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        can_generate_lectures: false,
        missing_keys: ['openrouter', 'elevenlabs'],
        setup_complete: false,
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    const statusSummary = await findByTestId('byok-status-summary');
    expect(statusSummary.props.children).toContain('Missing keys: openrouter, elevenlabs');

    const byokHint = await findByTestId('byok-settings-hint');
    expect(byokHint.props.children).toContain('BYOK is unavailable');

    fireEvent.press(getByTestId('generation-mode-environment'));
    const fallbackStatus = await findByTestId('fallback-status-message');
    expect(fallbackStatus.props.children).toContain('Fallback path active: Environment-managed providers');

    const providerCostCopy = await findByTestId('provider-cost-copy');
    expect(providerCostCopy.props.children).toContain('default budget path');
  });

  it('shows premium provider-cost copy when BYOK mode is active', async () => {
    const { findByTestId } = render(<CreateLectureScreen />);
    const providerCostCopy = await findByTestId('provider-cost-copy');
    expect(providerCostCopy.props.children).toContain('premium quality path');
  });

  it('renders script preview first, then confirms final generation', async () => {
    (lectureService.createLecture as jest.Mock)
      .mockResolvedValueOnce({
        success: true,
        data: {
          title: 'Dry Run Lecture Contract',
          script: 'Preview script content for confirmation.',
          preview_script: {
            title: 'Dry Run Lecture Contract',
            content: 'Preview script content for confirmation.',
            duration_minutes: 15,
            difficulty: 'beginner',
          },
          dry_run: true,
          key_source: 'environment',
        },
      })
      .mockResolvedValueOnce({
        success: true,
        data: {
          id: 'lecture-final-1',
          title: 'Generated Lecture',
          key_source: 'environment',
        },
      });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);

    fireEvent.changeText(getByTestId('topic-input'), 'Preview and confirm flow topic');
    fireEvent.press(getByTestId('create-lecture-button'));

    const previewCard = await findByTestId('script-preview-card');
    expect(previewCard).toBeTruthy();
    const previewText = await findByTestId('script-preview-text');
    expect(previewText.props.children).toBe('Preview script content for confirmation.');

    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalledTimes(2);
    });
    expect((lectureService.createLecture as jest.Mock).mock.calls[0][1].dryRun).toBe(true);
    expect((lectureService.createLecture as jest.Mock).mock.calls[1][1].dryRun).toBe(false);
  });

  it('submits file mode with inferred sourceType and upload file', async () => {
    const file = { name: 'outline.md', size: 2048, type: 'text/markdown' };

    Object.defineProperty(global, 'document', {
      value: {
        createElement: jest.fn(() => {
          const input: any = {
            type: 'file',
            accept: '',
            files: [file],
            onchange: null,
            click: function click() {
              if (typeof input.onchange === 'function') {
                input.onchange();
              }
            },
          };
          return input;
        }),
      },
      configurable: true,
    });

    const { getByTestId } = render(<CreateLectureScreen />);

    fireEvent.press(getByTestId('source-mode-file'));
    fireEvent.press(getByTestId('pick-file-button'));
    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });

    const [, options] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    expect(options.sourceType).toBe('md');
    expect(options.uploadFile).toBe(file);
  });

  it('renders URL diagnostics outcome: unreachable', async () => {
    (lectureService.diagnoseSourceUrl as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        success: false,
        schema: 'url-diagnostics-v1',
        contract_version: 'v1a',
        source_uri: 'https://bad.example.com',
        source_class: 'web',
        outcome: 'unreachable',
        diagnostics: {
          code: 'unreachable',
          message: 'URL could not be reached from the service. Check URL and try again.',
          retryable: true,
          status_code: null,
        },
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);
    fireEvent.press(getByTestId('source-mode-url'));
    fireEvent.changeText(getByTestId('url-input'), 'https://bad.example.com');
    fireEvent.press(getByTestId('run-url-diagnostics-button'));

    const codeNode = await findByTestId('url-diagnostics-code');
    expect(codeNode.props.children).toBe('unreachable');
  });

  it('renders URL diagnostics outcome: unsupported', async () => {
    (lectureService.diagnoseSourceUrl as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        success: false,
        schema: 'url-diagnostics-v1',
        contract_version: 'v1a',
        source_uri: 'https://open.spotify.com/episode/123',
        source_class: 'podcast',
        outcome: 'unsupported',
        diagnostics: {
          code: 'unsupported',
          message: 'Podcast/audio URL ingestion is deferred to the next slice.',
          retryable: false,
          status_code: 200,
        },
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);
    fireEvent.press(getByTestId('source-mode-url'));
    fireEvent.changeText(getByTestId('url-input'), 'https://open.spotify.com/episode/123');
    fireEvent.press(getByTestId('run-url-diagnostics-button'));

    const codeNode = await findByTestId('url-diagnostics-code');
    expect(codeNode.props.children).toBe('unsupported');
  });

  it('renders URL diagnostics outcome: no_transcript', async () => {
    (lectureService.diagnoseSourceUrl as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        success: false,
        schema: 'url-diagnostics-v1',
        contract_version: 'v1a',
        source_uri: 'https://www.youtube.com/watch?v=abc',
        source_class: 'video',
        outcome: 'no_transcript',
        diagnostics: {
          code: 'no_transcript',
          message: 'Video transcript ingestion is not enabled in this slice yet.',
          retryable: false,
          status_code: 200,
        },
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);
    fireEvent.press(getByTestId('source-mode-url'));
    fireEvent.changeText(getByTestId('url-input'), 'https://www.youtube.com/watch?v=abc');
    fireEvent.press(getByTestId('run-url-diagnostics-button'));

    const codeNode = await findByTestId('url-diagnostics-code');
    expect(codeNode.props.children).toBe('no_transcript');
  });

  it('keeps URL create blocked for non-ready outcome even when URL flag is enabled', async () => {
    process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1 = 'true';
    (lectureService.diagnoseSourceUrl as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        success: false,
        schema: 'url-diagnostics-v1',
        contract_version: 'v1a',
        source_uri: 'https://open.spotify.com/episode/blocked',
        source_class: 'podcast',
        outcome: 'unsupported',
        diagnostics: {
          code: 'unsupported',
          message: 'Podcast/audio URL ingestion is deferred to the next slice.',
          retryable: false,
          status_code: 200,
        },
      },
    });

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);
    fireEvent.press(getByTestId('source-mode-url'));
    fireEvent.changeText(getByTestId('url-input'), 'https://open.spotify.com/episode/blocked');
    fireEvent.press(getByTestId('run-url-diagnostics-button'));

    const codeNode = await findByTestId('url-diagnostics-code');
    expect(codeNode.props.children).toBe('unsupported');

    const createCallsBefore = (lectureService.createLecture as jest.Mock).mock.calls.length;
    fireEvent.press(getByTestId('create-lecture-button'));
    const createCallsAfter = (lectureService.createLecture as jest.Mock).mock.calls.length;
    expect(createCallsAfter).toBe(createCallsBefore);
  });

  it('renders URL diagnostics outcome: ready and submits when URL flag is enabled', async () => {
    process.env.EXPO_PUBLIC_ENABLE_URL_INGESTION_V1 = 'true';

    const { getByTestId, findByTestId } = render(<CreateLectureScreen />);
    fireEvent.press(getByTestId('source-mode-url'));
    fireEvent.changeText(getByTestId('url-input'), 'https://example.com/article');
    fireEvent.press(getByTestId('run-url-diagnostics-button'));

    const codeNode = await findByTestId('url-diagnostics-code');
    expect(codeNode.props.children).toBe('ready');

    fireEvent.press(getByTestId('create-lecture-button'));

    await waitFor(() => {
      expect(lectureService.createLecture).toHaveBeenCalled();
    });

    const [, options] = (lectureService.createLecture as jest.Mock).mock.calls[0];
    expect(options.sourceType).toBe('url');
    expect(options.sourceUrl).toBe('https://example.com/article');
  });
});
