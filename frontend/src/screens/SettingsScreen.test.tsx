import React from 'react';
import { fireEvent, render, waitFor } from '@testing-library/react-native';

import SettingsScreen from './SettingsScreen';
import lectureService from '../services/lecture';

jest.mock('../services/lecture', () => ({
  __esModule: true,
  default: {
    getApiKeyStatus: jest.fn(),
    storeApiKey: jest.fn(),
    validateApiKey: jest.fn(),
    deleteApiKey: jest.fn(),
  },
}));

describe('SettingsScreen BYOK status messaging', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(require('react-native').Alert, 'alert').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('shows fallback guidance when BYOK is incomplete', async () => {
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        can_generate_lectures: false,
        missing_keys: ['openrouter'],
        setup_complete: false,
        provider_status: {
          openrouter: {
            has_key: false,
            is_valid: false,
            last_used_at: null,
            last_validation_at: null,
            validation_error: null,
            usage_count: 0,
            key_name: null,
            last_validation_outcome: 'missing',
            remediation_hint: 'Add your openrouter key in Settings and run validation.',
          },
          elevenlabs: {
            has_key: true,
            is_valid: true,
            last_used_at: null,
            last_validation_at: '2026-04-14T00:00:00Z',
            validation_error: null,
            usage_count: 2,
            key_name: 'Primary ElevenLabs',
            last_validation_outcome: 'valid',
            remediation_hint: 'Key is valid and ready for generation.',
          },
        },
      },
    });

    const { getByTestId, getByText } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK not ready');
    });
    expect(getByTestId('settings-fallback-status').props.children).toContain('environment-managed providers');
    expect(getByTestId('settings-cost-default').props.children).toContain('Default budget path');
    expect(getByTestId('settings-cost-premium').props.children).toContain('Premium path');
    expect(getByText('OpenRouter - Missing')).toBeTruthy();
    expect(getByText('Add your openrouter key in Settings and run validation.')).toBeTruthy();
    expect(getByText('ElevenLabs - Valid')).toBeTruthy();
  });

  it('shows BYOK-ready guidance when required keys are complete', async () => {
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        can_generate_lectures: true,
        missing_keys: [],
        setup_complete: true,
        provider_status: {
          openrouter: {
            has_key: true,
            is_valid: true,
            last_used_at: null,
            last_validation_at: '2026-04-14T00:00:00Z',
            validation_error: null,
            usage_count: 1,
            key_name: 'Primary OpenRouter',
            last_validation_outcome: 'valid',
            remediation_hint: 'Key is valid and ready for generation.',
          },
          elevenlabs: {
            has_key: true,
            is_valid: true,
            last_used_at: null,
            last_validation_at: '2026-04-14T00:00:00Z',
            validation_error: null,
            usage_count: 2,
            key_name: 'Primary ElevenLabs',
            last_validation_outcome: 'valid',
            remediation_hint: 'Key is valid and ready for generation.',
          },
        },
      },
    });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK ready');
    });
    expect(getByTestId('settings-fallback-status').props.children).toContain('manual fallback');
    expect(getByTestId('settings-cost-default').props.children).toContain('Default budget path');
    expect(getByTestId('settings-cost-premium').props.children).toContain('Premium path');
  });

  it('refreshes provider status on user request', async () => {
    (lectureService.getApiKeyStatus as jest.Mock)
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: false,
          missing_keys: ['openrouter'],
          setup_complete: false,
        },
      })
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: true,
          missing_keys: [],
          setup_complete: true,
          provider_status: {
            openrouter: {
              has_key: true,
              is_valid: true,
              last_used_at: null,
              last_validation_at: '2026-04-14T00:00:00Z',
              validation_error: null,
              usage_count: 1,
              key_name: 'Primary OpenRouter',
              last_validation_outcome: 'valid',
              remediation_hint: 'Key is valid and ready for generation.',
            },
            elevenlabs: {
              has_key: true,
              is_valid: true,
              last_used_at: null,
              last_validation_at: '2026-04-14T00:00:00Z',
              validation_error: null,
              usage_count: 2,
              key_name: 'Primary ElevenLabs',
              last_validation_outcome: 'valid',
              remediation_hint: 'Key is valid and ready for generation.',
            },
          },
        },
      });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK not ready');
    });

    fireEvent.press(getByTestId('settings-refresh-key-status'));

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK ready');
    });
    expect(lectureService.getApiKeyStatus).toHaveBeenCalledTimes(2);
  });

  it('saves and validates an OpenRouter key from Settings key-entry controls', async () => {
    (lectureService.getApiKeyStatus as jest.Mock)
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: false,
          missing_keys: ['openrouter', 'elevenlabs'],
          setup_complete: false,
        },
      })
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: false,
          missing_keys: ['elevenlabs'],
          setup_complete: false,
        },
      });
    (lectureService.storeApiKey as jest.Mock).mockResolvedValueOnce({ success: true, data: { message: 'ok' } });
    (lectureService.validateApiKey as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: { is_valid: true, provider: 'openrouter', message: 'API key is valid' },
    });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK not ready');
    });

    fireEvent.changeText(getByTestId('settings-openrouter-key-input'), 'sk-or-v1-test-key');
    fireEvent.press(getByTestId('settings-openrouter-save-validate'));

    await waitFor(() => {
      expect(lectureService.storeApiKey).toHaveBeenCalledWith('openrouter', 'sk-or-v1-test-key');
    });
    expect(lectureService.validateApiKey).toHaveBeenCalledWith('openrouter');
    expect(lectureService.getApiKeyStatus).toHaveBeenCalledTimes(2);
  });

  it('deletes an ElevenLabs key from Settings key-entry controls', async () => {
    (lectureService.getApiKeyStatus as jest.Mock)
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: true,
          missing_keys: [],
          setup_complete: true,
          provider_status: {
            elevenlabs: {
              has_key: true,
              is_valid: true,
              last_used_at: null,
              last_validation_at: '2026-04-15T00:00:00Z',
              validation_error: null,
              usage_count: 1,
              key_name: 'Primary ElevenLabs',
              last_validation_outcome: 'valid',
              remediation_hint: 'Key is valid and ready for generation.',
            },
            openrouter: {
              has_key: true,
              is_valid: true,
              last_used_at: null,
              last_validation_at: '2026-04-15T00:00:00Z',
              validation_error: null,
              usage_count: 1,
              key_name: 'Primary OpenRouter',
              last_validation_outcome: 'valid',
              remediation_hint: 'Key is valid and ready for generation.',
            },
          },
        },
      })
      .mockResolvedValueOnce({
        success: true,
        data: {
          can_generate_lectures: false,
          missing_keys: ['elevenlabs'],
          setup_complete: false,
        },
      });
    (lectureService.deleteApiKey as jest.Mock).mockResolvedValueOnce({ success: true, data: { message: 'deleted' } });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK ready');
    });

    fireEvent.press(getByTestId('settings-elevenlabs-delete'));

    await waitFor(() => {
      expect(lectureService.deleteApiKey).toHaveBeenCalledWith('elevenlabs');
    });
    expect(lectureService.getApiKeyStatus).toHaveBeenCalledTimes(2);
  });
});
