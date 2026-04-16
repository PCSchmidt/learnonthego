import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, TextInputProps, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography } from '../../theme/tokens';

interface PremiumFieldProps extends TextInputProps {
  label: string;
  /** When true, adds a show/hide toggle for secureTextEntry */
  secureToggle?: boolean;
}

const PremiumField: React.FC<PremiumFieldProps> = ({ label, style, secureToggle, secureTextEntry, ...props }) => {
  const [hidden, setHidden] = useState(true);
  const isSecure = secureToggle ? hidden : secureTextEntry;

  return (
    <View style={styles.wrap}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.inputWrap}>
        <TextInput
          {...props}
          secureTextEntry={isSecure}
          style={[styles.input, secureToggle && styles.inputWithToggle, style]}
          placeholderTextColor={props.placeholderTextColor || '#7f8492'}
        />
        {secureToggle && (
          <Pressable
            onPress={() => setHidden((h) => !h)}
            style={styles.toggle}
            accessibilityRole="button"
            accessibilityLabel={hidden ? 'Show password' : 'Hide password'}
            hitSlop={8}
          >
            <Ionicons name={hidden ? 'eye-off-outline' : 'eye-outline'} size={20} color="#7f8492" />
          </Pressable>
        )}
      </View>
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
    flex: 1,
  },
  inputWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bg.cardLight,
    borderWidth: 1,
    borderColor: colors.border.light,
  },
  inputWithToggle: {
    borderWidth: 0,
    flex: 1,
  },
  toggle: {
    paddingHorizontal: spacing.sm,
    justifyContent: 'center',
    alignItems: 'center',
    height: 46,
  },
});

export default PremiumField;
