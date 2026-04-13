import { Platform } from 'react-native';

export const colors = {
  bg: {
    canvas: '#06070b',
    rail: '#0f131b',
    panel: '#f2f0ea',
    cardDark: '#111722',
    cardLight: '#f8f7f3',
  },
  text: {
    primaryDark: '#f4efe4',
    secondaryDark: '#aeb6c7',
    primaryLight: '#12151c',
    secondaryLight: '#4e5563',
    muted: '#7e8798',
  },
  border: {
    dark: '#242a37',
    medium: '#2b3240',
    light: '#b7bcc8',
    accent: '#a9905d',
  },
  accent: {
    brass: '#d7bf89',
    brassText: '#11151e',
    dangerBg: '#2a1115',
    dangerText: '#f2c6cf',
  },
  effect: {
    glowA: 'rgba(198, 168, 106, 0.08)',
    glowB: 'rgba(155, 166, 197, 0.08)',
  },
} as const;

export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 20,
  xl: 24,
  xxl: 34,
} as const;

// Premium direction is intentionally square-cornered.
export const radii = {
  none: 0,
} as const;

export const typography = {
  family: {
    body: Platform.OS === 'web' ? 'Manrope' : undefined,
    display: Platform.OS === 'web' ? 'Cormorant Garamond' : undefined,
  },
  size: {
    caption: 11,
    label: 12,
    body: 14,
    bodyLg: 16,
    heading: 28,
    display: 46,
  },
  letterSpacing: {
    tight: 0.2,
    normal: 0.8,
    wide: 1.8,
  },
  lineHeight: {
    body: 20,
    bodyLg: 24,
    heading: 32,
    display: 50,
  },
} as const;

export const surfaces = {
  shell: {
    borderWidth: 1,
    borderColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
  },
  panelDark: {
    borderWidth: 1,
    borderColor: colors.border.medium,
    backgroundColor: colors.bg.cardDark,
  },
  panelLight: {
    borderWidth: 1,
    borderColor: colors.border.light,
    backgroundColor: colors.bg.cardLight,
  },
} as const;
