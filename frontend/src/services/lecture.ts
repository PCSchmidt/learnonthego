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
  id: string;
  title: string;
  duration: number;
  audio_url: string;
  transcript?: string;
  created_at: string;
  status: 'generating' | 'completed' | 'failed';
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
  // Generate new lecture from text topic
  async generateLecture(request: LectureRequest): Promise<ApiResponse<LectureResponse>> {
    console.log('🎓 Generating lecture:', request.topic);
    
    const response = await apiClient.post<LectureResponse>('/api/lectures/generate', request);
    
    if (response.success) {
      console.log('✅ Lecture generation initiated:', response.data?.id);
    } else {
      console.error('❌ Lecture generation failed:', response.error);
    }
    
    return response;
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
