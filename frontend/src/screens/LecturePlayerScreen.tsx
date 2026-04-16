/**
 * LecturePlayerScreen - Functional audio player for generated lectures
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Audio, AVPlaybackStatus } from 'expo-av';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { colors, spacing, typography } from '../theme/tokens';
import PremiumButton from '../components/ui/PremiumButton';
import PremiumPanel from '../components/ui/PremiumPanel';

const STORAGE_KEY_TOKEN = '@LearnOnTheGo:accessToken';

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

type AudioState = 'idle' | 'loading' | 'playing' | 'paused' | 'error';

const LecturePlayerScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();

  const params = route.params as any;
  const lectureId = params?.lectureId || 'unknown';
  const audioUrl: string | null = params?.audioUrl || null;
  const lectureTitle: string = params?.title || 'Untitled Lecture';
  const script: string | null = params?.script || null;
  const citations: any[] = params?.citations || [];
  const sourceContext: any = params?.sourceContext || null;
  const duration: number | null = params?.duration || null;
  const difficulty: string | null = params?.difficulty || null;

  const soundRef = useRef<Audio.Sound | null>(null);
  const [audioState, setAudioState] = useState<AudioState>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [positionMs, setPositionMs] = useState(0);
  const [durationMs, setDurationMs] = useState(0);
  const [isSeeking, setIsSeeking] = useState(false);
  const seekValueRef = useRef(0);

  const onPlaybackStatusUpdate = useCallback((status: AVPlaybackStatus) => {
    if (!status.isLoaded) {
      if (status.error) {
        setAudioState('error');
        setErrorMessage(`Playback error: ${status.error}`);
      }
      return;
    }
    if (!isSeeking) {
      setPositionMs(status.positionMillis);
    }
    setDurationMs(status.durationMillis || 0);

    if (status.didJustFinish) {
      setAudioState('paused');
      setPositionMs(status.durationMillis || 0);
    } else if (status.isPlaying) {
      setAudioState('playing');
    } else if (status.isBuffering) {
      setAudioState('loading');
    } else {
      setAudioState('paused');
    }
  }, [isSeeking]);

  useEffect(() => {
    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
    };
  }, []);

  const loadAndPlay = async () => {
    if (!audioUrl) {
      setAudioState('error');
      setErrorMessage('No audio URL available for this lecture.');
      return;
    }

    setAudioState('loading');
    setErrorMessage(null);

    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }

      await Audio.setAudioModeAsync({
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
      });

      const token = await AsyncStorage.getItem(STORAGE_KEY_TOKEN);

      const { sound } = await Audio.Sound.createAsync(
        {
          uri: audioUrl,
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        },
        { shouldPlay: true, progressUpdateIntervalMillis: 250 },
        onPlaybackStatusUpdate
      );

      soundRef.current = sound;
    } catch (err) {
      setAudioState('error');
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load audio.');
    }
  };

  const togglePlayPause = async () => {
    if (!soundRef.current) {
      await loadAndPlay();
      return;
    }

    const status = await soundRef.current.getStatusAsync();
    if (!status.isLoaded) {
      await loadAndPlay();
      return;
    }

    if (status.didJustFinish || (status.durationMillis && status.positionMillis >= status.durationMillis)) {
      await soundRef.current.setPositionAsync(0);
      await soundRef.current.playAsync();
      return;
    }

    if (status.isPlaying) {
      await soundRef.current.pauseAsync();
    } else {
      await soundRef.current.playAsync();
    }
  };

  const seekTo = async (fraction: number) => {
    if (!soundRef.current || durationMs === 0) return;
    const target = Math.floor(fraction * durationMs);
    setPositionMs(target);
    await soundRef.current.setPositionAsync(target);
  };

  const handleSeekStart = () => setIsSeeking(true);

  const handleSeekEnd = (fraction: number) => {
    setIsSeeking(false);
    seekTo(fraction);
  };

  const progress = durationMs > 0 ? positionMs / durationMs : 0;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />

      <View style={styles.playerCard}>
        {/* Header Rail */}
        <View style={styles.headerRail}>
          <Text style={styles.eyebrow}>Now Playing</Text>
          <Text style={styles.headerTitle} numberOfLines={3}>{lectureTitle}</Text>
          {duration || difficulty ? (
            <Text style={styles.headerMeta}>
              {difficulty ? difficulty.charAt(0).toUpperCase() + difficulty.slice(1) : ''}
              {difficulty && duration ? ' · ' : ''}
              {duration ? `${duration} min` : ''}
            </Text>
          ) : null}
        </View>

        {/* Audio Controls Panel */}
        <View style={styles.controlsPanel}>
          {/* Player State */}
          {audioState === 'error' ? (
            <PremiumPanel dark={false} style={styles.errorPanel}>
              <Text style={styles.errorLabel}>Playback Error</Text>
              <Text style={styles.errorText}>{errorMessage}</Text>
            </PremiumPanel>
          ) : null}

          {!audioUrl ? (
            <PremiumPanel dark={false} style={styles.noAudioPanel}>
              <Text style={styles.noAudioLabel}>Audio Unavailable</Text>
              <Text style={styles.noAudioText}>
                This lecture was generated in preview mode or audio generation was not completed.
              </Text>
            </PremiumPanel>
          ) : (
            <>
              {/* Progress Bar */}
              <View style={styles.progressContainer}>
                <View
                  testID="player-progress-track"
                  style={styles.progressTrack}
                  {...(Platform.OS === 'web'
                    ? {
                        onClick: (e: any) => {
                          const rect = e.currentTarget.getBoundingClientRect();
                          const fraction = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                          handleSeekEnd(fraction);
                        },
                      }
                    : {})}
                  accessible
                  accessibilityRole="adjustable"
                  accessibilityLabel={`Playback progress: ${formatTime(positionMs)} of ${formatTime(durationMs)}`}
                  accessibilityHint="Tap to seek"
                >
                  <View
                    style={[styles.progressFill, { width: `${progress * 100}%` }]}
                  />
                  <View
                    style={[styles.progressThumb, { left: `${progress * 100}%` }]}
                  />
                </View>
                <View style={styles.timeRow}>
                  <Text style={styles.timeText}>{formatTime(positionMs)}</Text>
                  <Text style={styles.timeText}>{durationMs > 0 ? formatTime(durationMs) : '--:--'}</Text>
                </View>
              </View>

              {/* Play/Pause Button */}
              <View style={styles.controlsRow}>
                <PremiumButton
                  testID="player-play-pause-button"
                  title={
                    audioState === 'loading'
                      ? 'Loading...'
                      : audioState === 'playing'
                        ? 'Pause'
                        : audioState === 'idle'
                          ? 'Play'
                          : 'Resume'
                  }
                  onPress={togglePlayPause}
                  disabled={audioState === 'loading'}
                  variant="primary"
                  style={styles.playButton}
                />
              </View>

              {audioState === 'loading' ? (
                <ActivityIndicator
                  testID="player-loading-indicator"
                  size="small"
                  color={colors.accent.brass}
                  style={styles.loadingIndicator}
                />
              ) : null}
            </>
          )}
        </View>
      </View>

      {/* Script Section */}
      {script ? (
        <PremiumPanel dark eyebrow="Script" title={lectureTitle} style={styles.section}>
          <Text style={styles.scriptText}>{script}</Text>
        </PremiumPanel>
      ) : null}

      {/* Source Context & Citations */}
      {sourceContext || (Array.isArray(citations) && citations.length > 0) ? (
        <PremiumPanel
          dark={false}
          eyebrow="Source Context"
          style={styles.section}
          accessible
          accessibilityLabel="Source context"
          accessibilityHint="Shows source URI and citation references used for this lecture"
        >
          {sourceContext?.source_uri ? (
            <Text style={styles.sourceText}>Primary URI: {sourceContext.source_uri}</Text>
          ) : null}
          {sourceContext?.retrieval_method ? (
            <Text style={styles.sourceText}>Retrieval: {sourceContext.retrieval_method}</Text>
          ) : null}
          {sourceContext?.source_class ? (
            <Text style={styles.sourceText}>Class: {sourceContext.source_class}</Text>
          ) : null}
          {Array.isArray(citations)
            ? citations.map((citation: any, index: number) => (
                <Text
                  key={`${citation?.source_uri || 'source'}-${index}`}
                  style={styles.sourceText}
                >
                  — {citation?.source_uri || citation?.label || 'source-uri-unavailable'}
                </Text>
              ))
            : null}
        </PremiumPanel>
      ) : null}

      {/* Back Button */}
      <PremiumButton
        testID="player-back-home-button"
        title="Back to Home"
        onPress={() => navigation.goBack()}
        variant="secondary"
        style={styles.backButton}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg.canvas,
  },
  scrollContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xxl + spacing.xxl,
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -80,
    left: -70,
    width: 250,
    height: 250,
    backgroundColor: colors.effect.glowA,
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -80,
    right: -100,
    width: 280,
    height: 280,
    backgroundColor: colors.effect.glowB,
  },
  playerCard: {
    width: '100%',
    maxWidth: 1080,
    alignSelf: 'center',
    borderWidth: 1,
    borderColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
  },
  headerRail: {
    flex: Platform.OS === 'web' ? 0.9 : undefined,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
    borderBottomWidth: Platform.OS === 'web' ? 0 : 1,
    borderRightColor: colors.border.dark,
    borderBottomColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xl,
  },
  eyebrow: {
    color: colors.accent.brass,
    fontSize: typography.size.label,
    letterSpacing: typography.letterSpacing.wide,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: spacing.sm,
  },
  headerTitle: {
    fontSize: typography.size.heading,
    lineHeight: typography.lineHeight.heading,
    fontWeight: '600',
    color: colors.text.primaryDark,
    fontFamily: typography.family.display,
    marginBottom: spacing.xs,
  },
  headerMeta: {
    fontSize: typography.size.body,
    color: colors.text.secondaryDark,
  },
  controlsPanel: {
    flex: Platform.OS === 'web' ? 1.1 : undefined,
    backgroundColor: colors.bg.panel,
    padding: spacing.lg,
    justifyContent: 'center',
  },
  progressContainer: {
    marginBottom: spacing.md,
  },
  progressTrack: {
    height: 6,
    backgroundColor: colors.border.light,
    position: 'relative',
    cursor: Platform.OS === 'web' ? 'pointer' : undefined,
  } as any,
  progressFill: {
    position: 'absolute',
    top: 0,
    left: 0,
    height: 6,
    backgroundColor: colors.accent.brass,
  },
  progressThumb: {
    position: 'absolute',
    top: -5,
    width: 16,
    height: 16,
    backgroundColor: colors.accent.brass,
    borderWidth: 2,
    borderColor: colors.bg.panel,
    marginLeft: -8,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.xs,
  },
  timeText: {
    fontSize: typography.size.caption,
    color: colors.text.secondaryLight,
    letterSpacing: typography.letterSpacing.tight,
    fontVariant: ['tabular-nums'],
  },
  controlsRow: {
    alignItems: 'center',
  },
  playButton: {
    minWidth: 160,
  },
  loadingIndicator: {
    marginTop: spacing.sm,
  },
  errorPanel: {
    marginBottom: spacing.md,
    backgroundColor: colors.accent.dangerBg,
    borderColor: '#5f252f',
  },
  errorLabel: {
    fontSize: typography.size.label,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
    color: colors.accent.dangerText,
    marginBottom: spacing.xs,
  },
  errorText: {
    fontSize: typography.size.body,
    color: colors.accent.dangerText,
    lineHeight: typography.lineHeight.body,
  },
  noAudioPanel: {
    marginBottom: spacing.md,
  },
  noAudioLabel: {
    fontSize: typography.size.label,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
    color: colors.text.primaryLight,
    marginBottom: spacing.xs,
  },
  noAudioText: {
    fontSize: typography.size.body,
    color: colors.text.secondaryLight,
    lineHeight: typography.lineHeight.body,
  },
  section: {
    marginTop: spacing.lg,
    maxWidth: 1080,
    alignSelf: 'center',
    width: '100%',
  },
  scriptText: {
    fontSize: typography.size.body,
    lineHeight: typography.lineHeight.bodyLg,
    color: colors.text.secondaryDark,
  },
  sourceText: {
    fontSize: typography.size.body,
    color: colors.text.secondaryLight,
    lineHeight: typography.lineHeight.body,
    marginBottom: spacing.xxs,
  },
  backButton: {
    marginTop: spacing.xl,
    maxWidth: 1080,
    alignSelf: 'center',
    width: '100%',
  },
});

export default LecturePlayerScreen;
