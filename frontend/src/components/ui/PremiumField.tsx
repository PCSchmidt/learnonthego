import React from 'react';
import { StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';
import { colors, spacing, typography } from '../../theme/tokens';

interface PremiumFieldProps extends TextInputProps {
  label: string;
}

const PremiumField: React.FC<PremiumFieldProps> = ({ label, style, ...props }) => {
  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        {...props}
        style={[styles.input, style]}
        placeholderTextColor={props.placeholderTextColor || '#7f8492'}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: {
    marginBottom: spacing.md,
  },
  label: {
    color: '#2b3240',
    fontSize: typography.size.label,
    fontWeight: '700',
    letterSpacing: typography.letterSpacing.normal,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
  },
  input: {
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 46,
    fontSize: typography.size.bodyLg,
    color: '#0d1119',
  },
});

export default PremiumField;
