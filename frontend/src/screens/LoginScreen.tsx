/**
 * Login Screen - User authentication interface
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

interface LoginScreenProps {
  navigation: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const isWeb = Platform.OS === 'web';

  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      setErrorMessage('Please enter both email and password.');
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setErrorMessage(null);
    setIsLoading(true);

    try {
      const result = await login(email.trim(), password);

      if (result.success) {
        // Navigation will be handled by App.tsx when auth state changes
        Alert.alert('Success', 'Welcome back!');
      } else {
        const message = result.error || 'Please check your credentials';
        setErrorMessage(message);
        Alert.alert('Login Failed', message);
      }
    } catch (error) {
      setErrorMessage('Something went wrong. Please try again.');
      Alert.alert('Error', 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToRegister = () => {
    navigation.navigate('Register');
  };

  const handleForgotPassword = () => {
    Alert.alert(
      'Reset Password',
      'Password reset functionality will be available soon. Please contact support if needed.',
      [{ text: 'OK' }]
    );
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
            <Text style={styles.heroTitle}>Member Access</Text>
            <Text style={styles.heroCopy}>
              Access your personalized lecture intelligence system and continue building high-fidelity
              learning workflows.
            </Text>

            <View style={styles.metricBlock}>
              <Text style={styles.metricLabel}>Platform Positioning</Text>
              <Text style={styles.metricValue}>Exclusive AI Learning Suite</Text>
            </View>

            <View style={styles.metricBlock}>
              <Text style={styles.metricLabel}>Experience</Text>
              <Text style={styles.metricValue}>Precision Audio + Research Depth</Text>
            </View>
          </View>

          <View style={styles.formPanel}>
            <View style={styles.header}>
              <Text style={styles.eyebrow}>Secure Sign-In</Text>
              <Text style={styles.title}>Welcome Back</Text>
              <Text style={styles.subtitle}>Enter your credentials to access your workspace.</Text>
            </View>

            <View style={styles.form}>
              <PremiumField
                label="Email"
                testID="login-email-input"
                value={email}
                onChangeText={(value) => {
                  setEmail(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Email address"
                accessibilityHint="Enter the email for your LearnOnTheGo account"
                placeholder="name@company.com"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                editable={!isLoading}
              />

              <PremiumField
                label="Password"
                testID="login-password-input"
                value={password}
                onChangeText={(value) => {
                  setPassword(value);
                  if (errorMessage) {
                    setErrorMessage(null);
                  }
                }}
                accessibilityLabel="Password"
                accessibilityHint="Enter your account password"
                placeholder="Enter your password"
                secureTextEntry
                editable={!isLoading}
              />

              {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}

              <TouchableOpacity
                style={styles.forgotPassword}
                onPress={handleForgotPassword}
                accessibilityRole="button"
                accessibilityLabel="Forgot password"
                accessibilityHint="Opens password recovery guidance"
                disabled={isLoading}>
                <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
              </TouchableOpacity>

              <PremiumButton
                testID="login-submit-button"
                title="Enter Workspace"
                onPress={handleLogin}
                disabled={isLoading}
                loading={isLoading}
                accessibilityLabel="Enter workspace"
              />
            </View>

            <View style={styles.footer}>
              <Text style={styles.footerText}>No account yet?</Text>
              <TouchableOpacity onPress={navigateToRegister} disabled={isLoading}>
                <Text accessibilityRole="link" style={styles.footerLink}>Request Access</Text>
              </TouchableOpacity>
            </View>

            {isWeb ? (
              <Text style={styles.disclaimer}>Protected by enterprise-grade encryption and session controls.</Text>
            ) : null}
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
    minHeight: Platform.OS === 'web' ? 640 : undefined,
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
    fontSize: typography.size.display,
    lineHeight: typography.lineHeight.display,
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
  forgotPassword: {
    alignItems: 'flex-start',
    marginBottom: 22,
  },
  forgotPasswordText: {
    color: colors.text.secondaryLight,
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: typography.letterSpacing.tight,
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
    paddingTop: 6,
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
  disclaimer: {
    marginTop: spacing.sm,
    color: colors.text.muted,
    fontSize: typography.size.caption,
    letterSpacing: typography.letterSpacing.tight,
  },
});

export default LoginScreen;
