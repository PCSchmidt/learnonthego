/**
 * Multi-Provider AI Service - Interface for cost-optimized AI providers
 * Week 2: Frontend Integration for Multi-Provider Backend
 */

import apiClient, { ApiResponse } from './api';

// Provider Types
export type LLMProvider = 'openrouter' | 'openai_direct' | 'anthropic_direct';
export type TTSProvider = 'google_standard' | 'google_neural' | 'openai_tts' | 'elevenlabs' | 'unreal_speech';
export type QualityTier = 'free' | 'standard' | 'premium';

// API Request/Response Types
export interface MultiProviderLectureRequest {
  topic: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  preferred_llm_provider?: LLMProvider;
  preferred_tts_provider?: TTSProvider;
  quality_tier: QualityTier;
  use_cost_optimization: boolean;
}

export interface LectureResponse {
  id: string;
  title: string;
  content: string;
  audio_url: string;
  duration: number;
  llm_provider_used: LLMProvider;
  tts_provider_used: TTSProvider;
  estimated_cost: number;
  actual_cost: number;
  cost_savings: number;
  quality_tier: QualityTier;
  created_at: string;
}

export interface ProviderRecommendation {
  llm_provider: LLMProvider;
  tts_provider: TTSProvider;
  estimated_cost: number;
  quality_score: number;
  reasoning: string;
  cost_breakdown: {
    llm_cost: number;
    tts_cost: number;
    total_cost: number;
  };
}

export interface CostAnalysis {
  recommended_providers: ProviderRecommendation;
  all_options: ProviderRecommendation[];
  potential_savings: number;
  savings_percentage: number;
  free_tier_available: boolean;
}

export interface ProviderStatus {
  provider: string;
  status: 'healthy' | 'degraded' | 'down';
  response_time: number;
  last_checked: string;
  error_rate: number;
  capabilities: string[];
}

export interface UserAIPreferences {
  default_llm_provider?: LLMProvider;
  default_tts_provider?: TTSProvider;
  preferred_quality_tier: QualityTier;
  auto_optimize_costs: boolean;
  allow_fallback_providers: boolean;
  max_cost_per_lecture: number;
}

export interface AIProviderDashboardData {
  user_preferences: UserAIPreferences;
  provider_status: ProviderStatus[];
  usage_statistics: {
    total_lectures: number;
    total_cost: number;
    total_savings: number;
    average_cost_per_lecture: number;
  };
  recent_lectures: LectureResponse[];
}

/**
 * Multi-Provider AI Service Class
 */
class MultiProviderAIService {
  
  /**
   * Generate lecture using multi-provider system
   */
  async generateLecture(request: MultiProviderLectureRequest): Promise<ApiResponse<LectureResponse>> {
    return apiClient.post<LectureResponse>('/api/multi-provider/generate-lecture', request);
  }

  /**
   * Get cost analysis and provider recommendations
   */
  async getCostAnalysis(
    topic: string, 
    duration: number, 
    difficulty: string,
    qualityTier: QualityTier = 'standard'
  ): Promise<ApiResponse<CostAnalysis>> {
    return apiClient.post<CostAnalysis>('/api/multi-provider/analyze-costs', {
      topic,
      duration,
      difficulty,
      quality_tier: qualityTier,
    });
  }

  /**
   * Get provider recommendations for specific request
   */
  async getProviderRecommendations(
    topic: string,
    duration: number,
    difficulty: string,
    qualityTier: QualityTier = 'standard'
  ): Promise<ApiResponse<ProviderRecommendation[]>> {
    return apiClient.post<ProviderRecommendation[]>('/api/multi-provider/recommend-providers', {
      topic,
      duration,
      difficulty,
      quality_tier: qualityTier,
    });
  }

  /**
   * Get real-time provider status
   */
  async getProviderStatus(): Promise<ApiResponse<ProviderStatus[]>> {
    return apiClient.get<ProviderStatus[]>('/api/multi-provider/provider-status');
  }

  /**
   * Get user's AI preferences
   */
  async getUserPreferences(): Promise<ApiResponse<UserAIPreferences>> {
    return apiClient.get<UserAIPreferences>('/api/multi-provider/user-preferences');
  }

  /**
   * Update user's AI preferences
   */
  async updateUserPreferences(preferences: Partial<UserAIPreferences>): Promise<ApiResponse<UserAIPreferences>> {
    return apiClient.put<UserAIPreferences>('/api/multi-provider/user-preferences', preferences);
  }

  /**
   * Get comprehensive dashboard data
   */
  async getDashboardData(): Promise<ApiResponse<AIProviderDashboardData>> {
    return apiClient.get<AIProviderDashboardData>('/api/multi-provider/dashboard');
  }

  /**
   * Get available LLM models for a provider
   */
  async getAvailableModels(provider: LLMProvider): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>(`/api/multi-provider/llm-models/${provider}`);
  }

  /**
   * Get available TTS voices for a provider
   */
  async getAvailableVoices(provider: TTSProvider): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>(`/api/multi-provider/tts-voices/${provider}`);
  }

  /**
   * Test provider connectivity
   */
  async testProvider(providerType: 'llm' | 'tts', providerName: string): Promise<ApiResponse<ProviderStatus>> {
    return apiClient.post<ProviderStatus>('/api/multi-provider/test-provider', {
      provider_type: providerType,
      provider_name: providerName,
    });
  }

  /**
   * Get cost estimation without generating lecture
   */
  async estimateCost(
    topic: string,
    duration: number,
    llmProvider?: LLMProvider,
    ttsProvider?: TTSProvider
  ): Promise<ApiResponse<{estimated_cost: number, cost_breakdown: any}>> {
    return apiClient.post<{estimated_cost: number, cost_breakdown: any}>('/api/multi-provider/estimate-cost', {
      topic,
      duration,
      llm_provider: llmProvider,
      tts_provider: ttsProvider,
    });
  }
}

// Export singleton instance
export const multiProviderAIService = new MultiProviderAIService();
export default multiProviderAIService;
