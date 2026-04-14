/**
 * Lecture Service - Handles lecture generation and management
 * Integrates with backend AI pipeline for text/PDF to audio conversion
 */

import apiClient, { ApiResponse } from './api';

// Lecture Types
export interface LectureRequest {
  topic: string;
  duration: number; // minutes
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  voice: string;
  llmModelPreset?: ModelPresetId;
  llmModelId?: string;
  content_type?: 'text' | 'pdf';
  file_data?: string; // Base64 encoded PDF data
}

export type ModelPresetId = 'cost_saver' | 'balanced' | 'high_fidelity';

export interface ModelPreset {
  id: ModelPresetId;
  label: string;
  model: string;
  description: string;
}

export type SourceInputType = 'text' | 'txt' | 'md' | 'pdf' | 'url';

export interface SourceIntakeErrorDetail {
  schema?: string;
  code?:
    | 'unsupported_source_type'
    | 'invalid_source_input_combination'
    | 'source_type_input_mismatch'
    | 'unsupported_file_extension'
    | 'file_too_large'
    | 'invalid_text_encoding'
    | 'empty_text_content'
    | 'pdf_parse_failed'
    | 'url_ingestion_disabled'
    | 'url_not_ready'
    | 'url_fetch_failed'
    | 'empty_url_content'
    | string;
  message?: string;
  contract_version?: string;
  supported_source_types?: string[];
  field?: string;
  hint?: string;
  max_bytes?: number;
}

export interface LectureCreateOptions {
  useByok?: boolean;
  dryRun?: boolean;
  sourceType?: SourceInputType;
  uploadFile?: File;
  sourceUrl?: string;
}

export type UrlDiagnosticsOutcome = 'unreachable' | 'unsupported' | 'no_transcript' | 'ready';

export interface UrlDiagnosticsResponse {
  success: boolean;
  schema: 'url-diagnostics-v1';
  contract_version: string;
  source_uri: string;
  source_class: 'video' | 'podcast' | 'audio' | 'web' | 'unknown';
  outcome: UrlDiagnosticsOutcome;
  diagnostics: {
    code: UrlDiagnosticsOutcome;
    message: string;
    retryable: boolean;
    status_code?: number | null;
  };
}

export interface LectureResponse {
  id?: string;
  title: string;
  duration?: number;
  audio_url?: string;
  transcript?: string;
  created_at?: string;
  status?: 'generating' | 'completed' | 'failed';
  dry_run?: boolean;
  execution_mode?: 'environment' | 'byok';
  key_source?: 'environment' | 'user-encrypted-storage';
  source?: string;
  script?: string;
  summary?: string;
  preview_script?: {
    title: string;
    content: string;
    duration_minutes: number;
    difficulty: string;
  };
  script_sections?: Array<{
    id: string;
    heading: string;
    content: string;
  }>;
  citations?: Array<{
    label?: string;
    source_uri?: string;
    note?: string;
  }>;
  metadata?: {
    topic: string;
    difficulty: string;
    voice: string;
    word_count?: number;
    processing_time?: number;
  };
}

export interface LectureStatus {
  id: string;
  status: 'generating' | 'completed' | 'failed';
  progress?: number; // 0-100
  estimated_completion?: string;
  error_message?: string;
}

export interface ApiKeyStatus {
  can_generate_lectures: boolean;
  missing_keys: string[];
  setup_complete: boolean;
}

// Available Voices
export const AVAILABLE_VOICES = [
  { id: 'Rachel', name: 'Rachel (Professional Female)' },
  { id: 'Josh', name: 'Josh (Professional Male)' },
  { id: 'Arnold', name: 'Arnold (Authoritative Male)' },
  { id: 'Bella', name: 'Bella (Friendly Female)' },
  { id: 'Antoni', name: 'Antoni (Warm Male)' },
];

// Difficulty Levels
export const DIFFICULTY_LEVELS = [
  { id: 'beginner', name: 'Beginner', description: 'Basic concepts and simple explanations' },
  { id: 'intermediate', name: 'Intermediate', description: 'Moderate complexity with examples' },
  { id: 'advanced', name: 'Advanced', description: 'In-depth analysis and technical details' },
];

export const MODEL_PRESETS: ModelPreset[] = [
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
];

// Lecture Service Class
class LectureService {
  private mapSourceIntakeError(
    detail: SourceIntakeErrorDetail | undefined,
    fallback?: string
  ): string {
    if (!detail || detail.schema !== 'source-intake-error-v1') {
      return fallback || 'Failed to create lecture';
    }

    switch (detail.code) {
      case 'unsupported_source_type':
        return 'Source type is not supported in this slice. Use pasted text, .txt, .md, or .pdf.';
      case 'invalid_source_input_combination':
        return 'Select exactly one source input: pasted text or a single file.';
      case 'source_type_input_mismatch':
        return 'Selected source type does not match the provided input.';
      case 'unsupported_file_extension':
        return 'Unsupported file type. Allowed extensions: .txt, .md, .pdf.';
      case 'file_too_large':
        if (detail.max_bytes) {
          const mb = Math.max(1, Math.round(detail.max_bytes / (1024 * 1024)));
          return `File is too large. Maximum allowed size is ${mb}MB.`;
        }
        return 'File is too large for this source type.';
      case 'invalid_text_encoding':
        return 'Text files must be UTF-8 encoded.';
      case 'empty_text_content':
        return 'Uploaded text file is empty.';
      case 'pdf_parse_failed':
        return detail.message || 'Unable to extract content from PDF file.';
      case 'url_ingestion_disabled':
        return 'URL ingestion is currently disabled for this environment.';
      case 'url_not_ready':
        return detail.message || 'URL is not ready for generation. Run diagnostics and use a ready URL.';
      case 'url_fetch_failed':
        return detail.message || 'Failed to fetch URL content for generation.';
      case 'empty_url_content':
        return 'URL content was empty after extraction. Try a different article URL.';
      default:
        return detail.message || fallback || 'Failed to create lecture';
    }
  }

  // Generate new lecture from text topic using V2 endpoints.
  async generateLecture(
    request: LectureRequest,
    options?: LectureCreateOptions
  ): Promise<ApiResponse<LectureResponse>> {
    const useByok = Boolean(options?.useByok);
    const endpoint = useByok
      ? '/api/lectures/generate-document-v2-byok'
      : '/api/lectures/generate-document-v2';
    const sourceType = options?.sourceType || 'text';
    const sourceUrl = (options?.sourceUrl || '').trim();
    const selectedPreset = request.llmModelPreset || 'balanced';
    const presetModel = MODEL_PRESETS.find((preset) => preset.id === selectedPreset)?.model;
    const llmModel = request.llmModelId?.trim() || presetModel || 'anthropic/claude-3.5-sonnet';

    // Cost-aware default strategy:
    // - Environment path defaults to OpenAI TTS for lower-cost baseline.
    // - BYOK path keeps ElevenLabs as premium user-provided option.
    const ttsProvider = useByok ? 'elevenlabs' : 'openai';

    let response: ApiResponse<LectureResponse>;
    if (options?.uploadFile) {
      const multipart = new FormData();
      multipart.append('source_type', sourceType);
      multipart.append('duration', String(request.duration));
      multipart.append('difficulty', request.difficulty);
      multipart.append('llm_provider', 'openrouter');
      multipart.append('llm_model', llmModel);
      multipart.append('tts_provider', ttsProvider);
      multipart.append('voice_id', request.voice);
      multipart.append('dry_run', String(options?.dryRun ?? false));
      multipart.append('file', options.uploadFile);
      response = await apiClient.postMultipart<LectureResponse>(endpoint, multipart);
    } else {
      const formData: Record<string, string> = {
        source_type: sourceType,
        duration: String(request.duration),
        difficulty: request.difficulty,
        llm_provider: 'openrouter',
        llm_model: llmModel,
        tts_provider: ttsProvider,
        voice_id: request.voice,
        dry_run: String(options?.dryRun ?? false),
      };
      if (sourceType === 'url' && sourceUrl) {
        formData.source_uri = sourceUrl;
      } else {
        formData.document_text = request.topic;
      }
      response = await apiClient.postForm<LectureResponse>(endpoint, formData);
    }

    if (!response.success) {
      const detail = (response.errorDetails || undefined) as SourceIntakeErrorDetail | undefined;
      return {
        ...response,
        error: this.mapSourceIntakeError(detail, response.error),
      };
    }

    return response;
  }

  // Create new lecture (alias for generateLecture)
  async createLecture(
    request: LectureRequest,
    options?: LectureCreateOptions
  ): Promise<ApiResponse<LectureResponse>> {
    // Validate request first
    const validationErrors = this.validateLectureRequest(request, {
      hasUploadFile: Boolean(options?.uploadFile),
      hasSourceUrl: Boolean(options?.sourceUrl),
    });
    if (validationErrors.length > 0) {
      return {
        success: false,
        error: validationErrors.join(', '),
      };
    }

    return this.generateLecture(request, options);
  }

  // Generate lecture from PDF file
  async generateLectureFromPDF(
    file: { uri: string; name: string; type: string },
    options: Omit<LectureRequest, 'topic' | 'content_type' | 'file_data'>
  ): Promise<ApiResponse<LectureResponse>> {
    try {
      // In a real implementation, you'd convert the file to base64
      // For now, we'll use a placeholder
      const request: LectureRequest = {
        ...options,
        topic: `PDF: ${file.name}`,
        content_type: 'pdf',
        file_data: 'placeholder_base64_data', // TODO: Implement file conversion
      };

      return this.generateLecture(request);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'PDF processing error',
      };
    }
  }

  // Get lecture generation status
  async getLectureStatus(lectureId: string): Promise<ApiResponse<LectureStatus>> {
    return apiClient.get<LectureStatus>(`/api/lectures/${lectureId}/status`);
  }

  async getApiKeyStatus(): Promise<ApiResponse<ApiKeyStatus>> {
    return apiClient.get<ApiKeyStatus>('/api/api-keys/status');
  }

  async diagnoseSourceUrl(sourceUri: string): Promise<ApiResponse<UrlDiagnosticsResponse>> {
    const cleaned = (sourceUri || '').trim();
    if (!cleaned) {
      return {
        success: false,
        error: 'Enter a URL to run diagnostics.',
      };
    }

    return apiClient.postForm<UrlDiagnosticsResponse>('/api/lectures/url-diagnostics-v1', {
      source_uri: cleaned,
    });
  }

  // Get user's lecture library
  async getUserLectures(): Promise<ApiResponse<LectureResponse[]>> {
    return apiClient.get<LectureResponse[]>('/api/lectures/my-lectures');
  }

  // Get specific lecture details
  async getLecture(lectureId: string): Promise<ApiResponse<LectureResponse>> {
    return apiClient.get<LectureResponse>(`/api/lectures/${lectureId}`);
  }

  // Delete lecture
  async deleteLecture(lectureId: string): Promise<ApiResponse<{ message: string }>> {
    return apiClient.delete<{ message: string }>(`/api/lectures/${lectureId}`);
  }

  // Poll for lecture completion
  async pollLectureCompletion(
    lectureId: string,
    onProgress?: (status: LectureStatus) => void,
    maxAttempts: number = 60 // 5 minutes with 5-second intervals
  ): Promise<ApiResponse<LectureResponse>> {
    let attempts = 0;

    return new Promise((resolve) => {
      const poll = async () => {
        attempts++;

        const statusResponse = await this.getLectureStatus(lectureId);
        
        if (!statusResponse.success || !statusResponse.data) {
          resolve({
            success: false,
            error: 'Failed to get lecture status',
          });
          return;
        }

        const status = statusResponse.data;
        onProgress?.(status);

        if (status.status === 'completed') {
          const lectureResponse = await this.getLecture(lectureId);
          resolve(lectureResponse);
          return;
        }

        if (status.status === 'failed') {
          resolve({
            success: false,
            error: status.error_message || 'Lecture generation failed',
          });
          return;
        }

        if (attempts >= maxAttempts) {
          resolve({
            success: false,
            error: 'Lecture generation timeout',
          });
          return;
        }

        // Continue polling
        setTimeout(poll, 5000); // 5-second intervals
      };

      poll();
    });
  }

  // Validate lecture request
  validateLectureRequest(
    request: Partial<LectureRequest>,
    options?: { hasUploadFile?: boolean; hasSourceUrl?: boolean }
  ): string[] {
    const errors: string[] = [];
    const hasUploadFile = Boolean(options?.hasUploadFile);
    const hasSourceUrl = Boolean(options?.hasSourceUrl);

    if (!hasUploadFile && !hasSourceUrl && (!request.topic || request.topic.trim().length < 3)) {
      errors.push('Topic must be at least 3 characters long');
    }

    if (!request.duration || request.duration < 1 || request.duration > 60) {
      errors.push('Duration must be between 1 and 60 minutes');
    }

    if (!request.difficulty || !['beginner', 'intermediate', 'advanced'].includes(request.difficulty)) {
      errors.push('Please select a valid difficulty level');
    }

    if (!request.voice) {
      errors.push('Please select a voice');
    }

    return errors;
  }
}

// Export singleton instance
export const lectureService = new LectureService();
export default lectureService;
