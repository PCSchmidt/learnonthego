/**
 * Login Screen - User authentication interface
 * Integrates with backend authentication system
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

interface LoginScreenProps {
  navigation: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const isWeb = Platform.OS === 'web';

  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(email.trim(), password);

      if (result.success) {
        // Navigation will be handled by App.tsx when auth state changes
        Alert.alert('Success', 'Welcome back!');
      } else {
        Alert.alert('Login Failed', result.error || 'Please check your credentials');
      }
    } catch (error) {
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
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Email</Text>
                <TextInput
                  style={styles.input}
                  value={email}
                  onChangeText={setEmail}
                  placeholder="name@company.com"
                  placeholderTextColor="#7f8492"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  editable={!isLoading}
                />
              </View>

              <View style={styles.inputContainer}>
                <Text style={styles.label}>Password</Text>
                <TextInput
                  style={styles.input}
                  value={password}
                  onChangeText={setPassword}
                  placeholder="Enter your password"
                  placeholderTextColor="#7f8492"
                  secureTextEntry
                  editable={!isLoading}
                />
              </View>

              <TouchableOpacity
                style={styles.forgotPassword}
                onPress={handleForgotPassword}
                disabled={isLoading}>
                <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.loginButton, isLoading && styles.buttonDisabled]}
                onPress={handleLogin}
                disabled={isLoading}>
                {isLoading ? (
                  <ActivityIndicator color="#0a0a0a" />
                ) : (
                  <Text style={styles.loginButtonText}>Enter Workspace</Text>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.footer}>
              <Text style={styles.footerText}>No account yet?</Text>
              <TouchableOpacity onPress={navigateToRegister} disabled={isLoading}>
                <Text style={styles.footerLink}>Request Access</Text>
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
    backgroundColor: '#06070b',
  },
  backgroundGlowA: {
    position: 'absolute',
    top: -100,
    left: -60,
    width: 280,
    height: 280,
    backgroundColor: 'rgba(198, 168, 106, 0.09)',
  },
  backgroundGlowB: {
    position: 'absolute',
    bottom: -120,
    right: -90,
    width: 300,
    height: 300,
    backgroundColor: 'rgba(157, 171, 203, 0.08)',
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
    paddingVertical: 20,
  },
  shell: {
    width: '100%',
    maxWidth: 1160,
    alignSelf: 'center',
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    backgroundColor: '#0b0d12',
    borderWidth: 1,
    borderColor: '#242a37',
    minHeight: Platform.OS === 'web' ? 640 : undefined,
  },
  brandRail: {
    flex: 1,
    paddingHorizontal: 34,
    paddingVertical: 34,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
    borderBottomWidth: Platform.OS === 'web' ? 0 : 1,
    borderRightColor: '#242a37',
    borderBottomColor: '#242a37',
    backgroundColor: '#0f131b',
  },
  brand: {
    color: '#d7bf89',
    fontSize: 13,
    letterSpacing: 2.1,
    textTransform: 'uppercase',
    fontWeight: '700',
    marginBottom: 10,
  },
  brandSubhead: {
    color: '#8d96a8',
    fontSize: 12,
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginBottom: 38,
  },
  heroTitle: {
    color: '#f5efe3',
    fontSize: 52,
    lineHeight: 56,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 14,
  },
  heroCopy: {
    color: '#b1b7c5',
    fontSize: 16,
    lineHeight: 24,
    maxWidth: 460,
    marginBottom: 34,
  },
  metricBlock: {
    borderTopWidth: 1,
    borderTopColor: '#2a3140',
    paddingTop: 14,
    marginBottom: 14,
  },
  metricLabel: {
    color: '#7e8798',
    fontSize: 11,
    letterSpacing: 1.3,
    textTransform: 'uppercase',
    marginBottom: 7,
  },
  metricValue: {
    color: '#d8dde8',
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
  },
  formPanel: {
    flex: 1,
    backgroundColor: '#f2f0ea',
    paddingHorizontal: 34,
    paddingVertical: 34,
  },
  header: {
    marginBottom: 24,
  },
  eyebrow: {
    fontSize: 11,
    letterSpacing: 1.4,
    textTransform: 'uppercase',
    color: '#6f6450',
    fontWeight: '700',
    marginBottom: 8,
  },
  title: {
    color: '#12151c',
    fontSize: 46,
    lineHeight: 50,
    fontWeight: '600',
    fontFamily: 'Cormorant Garamond',
    marginBottom: 8,
  },
  subtitle: {
    color: '#4e5563',
    fontSize: 16,
    lineHeight: 22,
  },
  form: {
    marginBottom: 20,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    color: '#2b3240',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f8f7f3',
    borderWidth: 1,
    borderColor: '#b7bcc8',
    paddingHorizontal: 16,
    paddingVertical: 13,
    fontSize: 16,
    color: '#0d1119',
  },
  forgotPassword: {
    alignItems: 'flex-start',
    marginBottom: 22,
  },
  forgotPasswordText: {
    color: '#5f6777',
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.2,
  },
  loginButton: {
    backgroundColor: '#d7bf89',
    borderWidth: 1,
    borderColor: '#a9905d',
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  loginButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#11151e',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#c5c9d2',
    marginTop: 8,
  },
  footerText: {
    color: '#4c5464',
    fontSize: 14,
    paddingTop: 10,
  },
  footerLink: {
    color: '#171e2a',
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    paddingTop: 10,
  },
  disclaimer: {
    marginTop: 12,
    color: '#636a78',
    fontSize: 11,
    letterSpacing: 0.2,
  },
});

export default LoginScreen;
