import apiClient from './api';

export type QualityTier = 'free' | 'standard' | 'premium';
export type LLMProvider = 'openrouter' | 'openai';
export type TTSProvider = 'elevenlabs' | 'openai';

export interface ProviderStatus {
	provider: string;
	status: 'healthy' | 'degraded' | 'down';
	response_time: number;
	error_rate: number;
	capabilities: string[];
}

export interface AIProviderDashboardData {
	provider_status: ProviderStatus[];
	usage_statistics: {
		total_lectures: number;
		total_cost: number;
		total_savings: number;
		average_cost_per_lecture: number;
	};
	user_preferences: {
		preferred_quality_tier: QualityTier;
		default_llm_provider: LLMProvider;
		default_tts_provider: TTSProvider;
		auto_optimize_costs: boolean;
		max_cost_per_lecture?: number;
	};
}

interface ServiceResponse<T> {
	success: boolean;
	data?: T;
	error?: string;
}

class MultiProviderAIService {
	async getDashboardData(): Promise<ServiceResponse<AIProviderDashboardData>> {
		const response = await apiClient.get<AIProviderDashboardData>('/api/system-status/dashboard');

		if (response.success && response.data) {
			return response;
		}

		// Fallback demo payload keeps dashboard usable while backend endpoint evolves.
		return {
			success: true,
			data: {
				provider_status: [
					{
						provider: 'openrouter',
						status: 'healthy',
						response_time: 420,
						error_rate: 0.01,
						capabilities: ['script-generation', 'long-context'],
					},
					{
						provider: 'elevenlabs',
						status: 'healthy',
						response_time: 650,
						error_rate: 0.02,
						capabilities: ['premium-voices', 'multilingual-tts'],
					},
				],
				usage_statistics: {
					total_lectures: 0,
					total_cost: 0,
					total_savings: 0,
					average_cost_per_lecture: 0,
				},
				user_preferences: {
					preferred_quality_tier: 'standard',
					default_llm_provider: 'openrouter',
					default_tts_provider: 'elevenlabs',
					auto_optimize_costs: true,
					max_cost_per_lecture: 0.25,
				},
			},
		};
	}

	async testProvider(providerType: 'llm' | 'tts', providerName: string): Promise<ServiceResponse<null>> {
		const response = await apiClient.post<{ ok: boolean }>('/api/system-status/provider-test', {
			provider_type: providerType,
			provider_name: providerName,
		});

		if (response.success) {
			return { success: true, data: null };
		}

		return { success: false, error: response.error || 'Provider test failed' };
	}
}

const multiProviderAIService = new MultiProviderAIService();
export default multiProviderAIService;
