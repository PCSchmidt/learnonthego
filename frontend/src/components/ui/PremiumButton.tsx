import React from 'react';
import { Pressable, StyleSheet, Text, TextStyle, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme/tokens';

type ButtonVariant = 'primary' | 'secondary' | 'danger';

interface PremiumButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
  style?: ViewStyle;
}

const variantStyles: Record<ButtonVariant, { container: ViewStyle; text: TextStyle }> = {
  primary: {
    container: {
      backgroundColor: colors.accent.brass,
      borderColor: colors.border.accent,
    },
    text: {
      color: colors.accent.brassText,
    },
  },
  secondary: {
    container: {
      backgroundColor: colors.bg.cardDark,
      borderColor: colors.border.medium,
    },
    text: {
      color: colors.text.primaryDark,
    },
  },
  danger: {
    container: {
      backgroundColor: colors.accent.dangerBg,
      borderColor: '#5f252f',
    },
    text: {
      color: colors.accent.dangerText,
    },
  },
};

const PremiumButton: React.FC<PremiumButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  style,
}) => {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.base,
        variantStyles[variant].container,
        pressed && !disabled ? styles.pressed : null,
        disabled ? styles.disabled : null,
        style,
      ]}
    >
      <Text style={[styles.textBase, variantStyles[variant].text]}>{title}</Text>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  base: {
    minHeight: 48,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  textBase: {
    fontSize: typography.size.label,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
  },
  pressed: {
    opacity: 0.9,
  },
  disabled: {
    opacity: 0.5,
  },
});

export default PremiumButton;
