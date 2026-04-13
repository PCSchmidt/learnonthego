import React from 'react';
import { StyleSheet, Text, View, ViewProps } from 'react-native';
import { colors, spacing, typography } from '../../theme/tokens';

interface PremiumPanelProps extends ViewProps {
  title?: string;
  eyebrow?: string;
  dark?: boolean;
}

const PremiumPanel: React.FC<PremiumPanelProps> = ({
  title,
  eyebrow,
  dark = true,
  style,
  children,
  ...rest
}) => {
  return (
    <View style={[styles.base, dark ? styles.dark : styles.light, style]} {...rest}>
      {eyebrow ? <Text style={[styles.eyebrow, dark ? styles.eyebrowDark : styles.eyebrowLight]}>{eyebrow}</Text> : null}
      {title ? <Text style={[styles.title, dark ? styles.titleDark : styles.titleLight]}>{title}</Text> : null}
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  base: {
    borderWidth: 1,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  dark: {
    backgroundColor: colors.bg.cardDark,
    borderColor: colors.border.medium,
  },
  light: {
    backgroundColor: colors.bg.cardLight,
    borderColor: colors.border.light,
  },
  eyebrow: {
    fontSize: typography.size.caption,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.wide,
    marginBottom: spacing.sm,
  },
  eyebrowDark: {
    color: colors.text.muted,
  },
  eyebrowLight: {
    color: '#6f6450',
  },
  title: {
    fontSize: typography.size.heading,
    lineHeight: typography.lineHeight.heading,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: spacing.md,
  },
  titleDark: {
    color: colors.text.primaryDark,
  },
  titleLight: {
    color: colors.text.primaryLight,
  },
});

export default PremiumPanel;
