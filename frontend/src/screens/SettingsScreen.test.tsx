import React from 'react';
import { render, waitFor } from '@testing-library/react-native';

import SettingsScreen from './SettingsScreen';
import lectureService from '../services/lecture';

jest.mock('../services/lecture', () => ({
  __esModule: true,
  default: {
    getApiKeyStatus: jest.fn(),
  },
}));

describe('SettingsScreen BYOK status messaging', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows fallback guidance when BYOK is incomplete', async () => {
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        can_generate_lectures: false,
        missing_keys: ['openrouter'],
        setup_complete: false,
      },
    });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK not ready');
    });
    expect(getByTestId('settings-fallback-status').props.children).toContain('environment-managed providers');
  });

  it('shows BYOK-ready guidance when required keys are complete', async () => {
    (lectureService.getApiKeyStatus as jest.Mock).mockResolvedValueOnce({
      success: true,
      data: {
        can_generate_lectures: true,
        missing_keys: [],
        setup_complete: true,
      },
    });

    const { getByTestId } = render(<SettingsScreen />);

    await waitFor(() => {
      expect(getByTestId('settings-byok-status').props.children).toContain('BYOK ready');
    });
    expect(getByTestId('settings-fallback-status').props.children).toContain('manual fallback');
  });
});
