/**
 * Register Screen - User registration interface
 * Integrates with backend authentication system
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { colors, spacing, typography } from '../theme/tokens';
import PremiumButton from '../components/ui/PremiumButton';
import PremiumField from '../components/ui/PremiumField';

interface RegisterScreenProps {
  navigation: any;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();

  const validateForm = () => {
    if (!fullName.trim()) {
      setErrorMessage('Please enter your full name.');
      Alert.alert('Error', 'Please enter your full name');
      return false;
    }

    if (!email.trim()) {
      setErrorMessage('Please enter your email.');
      Alert.alert('Error', 'Please enter your email');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setErrorMessage('Please enter a valid email address.');
      Alert.alert('Error', 'Please enter a valid email address');
      return false;
    }

    if (!password.trim()) {
      setErrorMessage('Please enter a password.');
      Alert.alert('Error', 'Please enter a password');
      return false;
    }

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      Alert.alert('Error', 'Password must be at least 8 characters long');
      return false;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match.');
      Alert.alert('Error', 'Passwords do not match');
      return false;
    }

    return true;
  };

  const handleRegister = async () => {
    setErrorMessage(null);
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await register(email.trim(), password, confirmPassword, fullName.trim());

      if (result.success) {
        Alert.alert('Success', 'Account created successfully! Welcome to LearnOnTheGo!');
        // Navigation will be handled by App.tsx when auth state changes
      } else {
        const message = result.error || 'Please try again';
        setErrorMessage(message);
        Alert.alert('Registration Failed', message);
      }
    } catch (error) {
      setErrorMessage('Something went wrong. Please try again.');
      Alert.alert('Error', 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToLogin = () => {
    navigation.navigate('Login');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.backgroundGlowA} />
      <View style={styles.backgroundGlowB} />
      <View style={styles.gridLineVertical} />
      <View style={styles.gridLineHorizontal} />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.shell}>
          <View style={styles.brandRail}>
            <Text style={styles.brand}>LearnOnTheGo</Text>
            <Text style={styles.brandSubhead}>Private Learning Intelligence</Text>
            <Text style={styles.heroTitle}>Admission Request</Text>
            <Text style={styles.heroCopy}>
              Create your account to access an elite workspace for AI-guided learning, research depth,
              and premium audio education delivery.
            </Text>

            <View style={styles.metricBlock}>
              <Text style={styles.metricLabel}>Onboarding Profile</Text>
              <Text style={styles.metricValue}>Professional + Graduate-Level Learning</Text>
            </View>

            <View style={styles.metricBlock}>
              <Text style={styles.metricLabel}>Activation</Text>
              <Text style={styles.metricValue}>Instant account provisioning and secure access</Text>
            </View>
          </View>

          <View style={styles.formPanel}>
            <View style={styles.header}>
              <Text style={styles.eyebrow}>Create Secure Profile</Text>
              <Text style={styles.title}>Create Account</Text>
              <Text style={styles.subtitle}>Set up your membership credentials in under a minute.</Text>
            </View>

            <View style={styles.form}>
              <PremiumField
                label="Full Name"
                testID="register-full-name-input"
                value={fullName}
                onChangeText={(value) => {
                  setFullName(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Full name"
                accessibilityHint="Enter your full name for account setup"
                placeholder="Your full name"
                autoCapitalize="words"
                editable={!isLoading}
              />

              <PremiumField
                label="Email"
                testID="register-email-input"
                value={email}
                onChangeText={(value) => {
                  setEmail(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Email address"
                accessibilityHint="Enter the email you want to use for this account"
                placeholder="name@company.com"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                editable={!isLoading}
              />

              <PremiumField
                label="Password"
                testID="register-password-input"
                value={password}
                onChangeText={(value) => {
                  setPassword(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Password"
                accessibilityHint="Enter a password with at least 8 characters"
                placeholder="Minimum 8 characters"
                secureToggle
                editable={!isLoading}
              />

              <PremiumField
                label="Confirm Password"
                testID="register-confirm-password-input"
                value={confirmPassword}
                onChangeText={(value) => {
                  setConfirmPassword(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Confirm password"
                accessibilityHint="Re-enter the same password to confirm"
                placeholder="Re-enter password"
                secureToggle
                editable={!isLoading}
              />

              {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}

              <PremiumButton
                testID="register-submit-button"
                title="Create Membership"
                onPress={handleRegister}
                disabled={isLoading}
                loading={isLoading}
                accessibilityLabel="Create membership"
              />
            </View>

            <View style={styles.footer}>
              <Text style={styles.footerText}>Already have access?</Text>
              <TouchableOpacity onPress={navigateToLogin} disabled={isLoading}>
                <Text accessibilityRole="link" style={styles.footerLink}>Sign In</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.termsContainer}>
              <Text style={styles.termsText}>
                By creating an account, you agree to Terms of Service and Privacy Policy.
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg.canvas,
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -100,
    left: -60,
    width: 280,
    height: 280,
    backgroundColor: colors.effect.glowA,
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -120,
    right: -90,
    width: 300,
    height: 300,
    backgroundColor: colors.effect.glowB,
  },
  gridLineVertical: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: '62%',
    width: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
  },
  gridLineHorizontal: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: '18%',
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 18,
    paddingVertical: spacing.lg,
  },
  shell: {
    width: '100%',
    maxWidth: 1160,
    alignSelf: 'center',
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    backgroundColor: '#0b0d12',
    borderWidth: 1,
    borderColor: colors.border.dark,
    minHeight: Platform.OS === 'web' ? 660 : undefined,
  },
  brandRail: {
    flex: 1,
    paddingHorizontal: spacing.xxl,
    paddingVertical: spacing.xxl,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
    borderBottomWidth: Platform.OS === 'web' ? 0 : 1,
    borderRightColor: colors.border.dark,
    borderBottomColor: colors.border.dark,
    backgroundColor: colors.bg.rail,
  },
  brand: {
    color: colors.accent.brass,
    fontSize: 13,
    letterSpacing: 2.1,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 10,
  },
  brandSubhead: {
    color: colors.text.muted,
    fontSize: typography.size.label,
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginBottom: 38,
  },
  heroTitle: {
    color: colors.text.primaryDark,
    fontSize: 52,
    lineHeight: 56,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: 14,
  },
  heroCopy: {
    color: colors.text.secondaryDark,
    fontSize: typography.size.bodyLg,
    lineHeight: typography.lineHeight.bodyLg,
    maxWidth: 460,
    marginBottom: spacing.xxl,
  },
  metricBlock: {
    borderTopWidth: 1,
    borderTopColor: colors.border.medium,
    paddingTop: 14,
    marginBottom: 14,
  },
  metricLabel: {
    color: colors.text.muted,
    fontSize: typography.size.caption,
    letterSpacing: 1.3,
    textTransform: 'uppercase',
    marginBottom: 7,
  },
  metricValue: {
    color: '#d8dde8',
    fontSize: 15,
    lineHeight: typography.lineHeight.body,
    fontWeight: '600',
  },
  formPanel: {
    flex: 1,
    backgroundColor: colors.bg.panel,
    paddingHorizontal: spacing.xxl,
    paddingVertical: spacing.xxl,
  },
  header: {
    marginBottom: spacing.xl,
  },
  eyebrow: {
    fontSize: typography.size.caption,
    letterSpacing: 1.4,
    textTransform: 'uppercase',
    color: '#6f6450',
    fontWeight: '700',
    marginBottom: spacing.xs,
  },
  title: {
    color: colors.text.primaryLight,
    fontSize: 44,
    lineHeight: 48,
    fontWeight: '600',
    fontFamily: typography.family.display,
    marginBottom: spacing.xs,
  },
  subtitle: {
    color: colors.text.secondaryLight,
    fontSize: typography.size.bodyLg,
    lineHeight: 22,
  },
  form: {
    marginBottom: spacing.lg,
  },
  errorText: {
    color: '#8f1d1d',
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 14,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
    borderTopWidth: 1,
    borderTopColor: colors.border.light,
    marginTop: spacing.xs,
  },
  footerText: {
    color: colors.text.secondaryLight,
    fontSize: typography.size.body,
    paddingTop: 10,
  },
  footerLink: {
    color: colors.text.primaryLight,
    fontSize: typography.size.body,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: typography.letterSpacing.normal,
    paddingTop: 10,
  },
  termsContainer: {
    borderTopWidth: 1,
    borderTopColor: colors.border.light,
    paddingTop: 10,
  },
  termsText: {
    color: colors.text.muted,
    fontSize: typography.size.caption,
    lineHeight: 16,
  },
});

export default RegisterScreen;
