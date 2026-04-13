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
  content_type?: 'text' | 'pdf';
  file_data?: string; // Base64 encoded PDF data
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
  key_source?: 'environment' | 'user-encrypted-storage';
  source?: string;
  script?: string;
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

// Lecture Service Class
class LectureService {
  // Generate new lecture from text topic using V2 endpoints.
  async generateLecture(
    request: LectureRequest,
    options?: { useByok?: boolean; dryRun?: boolean }
  ): Promise<ApiResponse<LectureResponse>> {
    const useByok = Boolean(options?.useByok);
    const endpoint = useByok
      ? '/api/lectures/generate-document-v2-byok'
      : '/api/lectures/generate-document-v2';

    // Cost-aware default strategy:
    // - Environment path defaults to OpenAI TTS for lower-cost baseline.
    // - BYOK path keeps ElevenLabs as premium user-provided option.
    const ttsProvider = useByok ? 'elevenlabs' : 'openai';

    const formData: Record<string, string> = {
      document_text: request.topic,
      duration: String(request.duration),
      difficulty: request.difficulty,
      llm_provider: 'openrouter',
      tts_provider: ttsProvider,
      voice_id: request.voice,
      dry_run: String(options?.dryRun ?? false),
    };

    return apiClient.postForm<LectureResponse>(endpoint, formData);
  }

  // Create new lecture (alias for generateLecture)
  async createLecture(
    request: LectureRequest,
    options?: { useByok?: boolean; dryRun?: boolean }
  ): Promise<ApiResponse<LectureResponse>> {
    // Validate request first
    const validationErrors = this.validateLectureRequest(request);
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
  validateLectureRequest(request: Partial<LectureRequest>): string[] {
    const errors: string[] = [];

    if (!request.topic || request.topic.trim().length < 3) {
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
