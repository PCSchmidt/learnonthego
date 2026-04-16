import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';

const mockGoBack = jest.fn();

jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    goBack: mockGoBack,
  }),
  useRoute: () => ({
    params: mockRouteParams,
  }),
}));

jest.mock('expo-av', () => {
  const mockSound = {
    getStatusAsync: jest.fn().mockResolvedValue({ isLoaded: true, isPlaying: false, positionMillis: 0, durationMillis: 60000 }),
    playAsync: jest.fn().mockResolvedValue({}),
    pauseAsync: jest.fn().mockResolvedValue({}),
    setPositionAsync: jest.fn().mockResolvedValue({}),
    unloadAsync: jest.fn().mockResolvedValue({}),
  };
  return {
    Audio: {
      Sound: {
        createAsync: jest.fn().mockResolvedValue({ sound: mockSound }),
      },
      setAudioModeAsync: jest.fn().mockResolvedValue(undefined),
    },
  };
});

jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn().mockResolvedValue('mock-jwt-token'),
}));

import LecturePlayerScreen from './LecturePlayerScreen';

let mockRouteParams: any = {};

describe('LecturePlayerScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockRouteParams = {
      lectureId: 'test-123',
      audioUrl: 'https://example.com/api/lectures/audio/v2/test.mp3',
      title: 'Introduction to TypeScript',
      script: 'TypeScript is a typed superset of JavaScript.',
      citations: [{ source_uri: 'https://typescriptlang.org', label: 'TS Docs' }],
      sourceContext: { source_uri: 'https://typescriptlang.org', retrieval_method: 'web_fetch', source_class: 'web' },
      duration: 15,
      difficulty: 'beginner',
    };
  });

  it('renders lecture title and metadata', () => {
    const { getAllByText, getByText } = render(<LecturePlayerScreen />);
    expect(getAllByText('Introduction to TypeScript').length).toBeGreaterThanOrEqual(1);
    expect(getByText('Beginner · 15 min')).toBeTruthy();
  });

  it('renders play button when audio URL is provided', () => {
    const { getByTestId } = render(<LecturePlayerScreen />);
    expect(getByTestId('player-play-pause-button')).toBeTruthy();
  });

  it('renders script section', () => {
    const { getByText } = render(<LecturePlayerScreen />);
    expect(getByText('TypeScript is a typed superset of JavaScript.')).toBeTruthy();
  });

  it('renders source context and citations', () => {
    const { getByText } = render(<LecturePlayerScreen />);
    expect(getByText('Primary URI: https://typescriptlang.org')).toBeTruthy();
    expect(getByText('Retrieval: web_fetch')).toBeTruthy();
    expect(getByText('Class: web')).toBeTruthy();
    expect(getByText('— https://typescriptlang.org')).toBeTruthy();
  });

  it('shows no-audio state when audioUrl is null', () => {
    mockRouteParams = { ...mockRouteParams, audioUrl: null };
    const { getByText, queryByTestId } = render(<LecturePlayerScreen />);
    expect(getByText('Audio Unavailable')).toBeTruthy();
    expect(queryByTestId('player-play-pause-button')).toBeNull();
  });

  it('navigates back when back button is pressed', () => {
    const { getByTestId } = render(<LecturePlayerScreen />);
    fireEvent.press(getByTestId('player-back-home-button'));
    expect(mockGoBack).toHaveBeenCalledTimes(1);
  });

  it('renders time display with initial values', () => {
    const { getByText } = render(<LecturePlayerScreen />);
    expect(getByText('0:00')).toBeTruthy();
    expect(getByText('--:--')).toBeTruthy();
  });

  it('loads and plays audio on play button press', async () => {
    const { Audio } = require('expo-av');
    const { getByTestId } = render(<LecturePlayerScreen />);

    fireEvent.press(getByTestId('player-play-pause-button'));

    await waitFor(() => {
      expect(Audio.setAudioModeAsync).toHaveBeenCalled();
      expect(Audio.Sound.createAsync).toHaveBeenCalledWith(
        {
          uri: 'https://example.com/api/lectures/audio/v2/test.mp3',
          headers: { Authorization: 'Bearer mock-jwt-token' },
        },
        { shouldPlay: true, progressUpdateIntervalMillis: 250 },
        expect.any(Function)
      );
    });
  });

  it('renders with minimal params (only lectureId)', () => {
    mockRouteParams = { lectureId: 'minimal-1' };
    const { getByText } = render(<LecturePlayerScreen />);
    expect(getByText('Untitled Lecture')).toBeTruthy();
    expect(getByText('Audio Unavailable')).toBeTruthy();
  });
});
