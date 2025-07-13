import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ScrollView, Alert } from 'react-native';

const App: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleEarlyAccess = async () => {
    if (!email) {
      Alert.alert('Email Required', 'Please enter your email to join the early access list.');
      return;
    }
    
    if (!email.includes('@')) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    // TODO: Integrate with email signup service
    setTimeout(() => {
      Alert.alert('Success!', 'You\'ve been added to our early access list. We\'ll notify you when LearnOnTheGo launches!');
      setEmail('');
      setIsSubmitting(false);
    }, 1500);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <Text style={styles.heroEmoji}>🎓</Text>
        <Text style={styles.heroTitle}>LearnOnTheGo</Text>
        <Text style={styles.heroSubtitle}>Transform Any Topic Into Audio Lectures</Text>
        <Text style={styles.heroDescription}>
          Convert text topics or PDF documents into personalized, professional audio lectures. 
          Perfect for learning during commutes, workouts, or walks.
        </Text>
        
        {/* Early Access Form */}
        <View style={styles.earlyAccessContainer}>
          <Text style={styles.earlyAccessTitle}>Get Early Access</Text>
          <View style={styles.emailContainer}>
            <TextInput
              style={styles.emailInput}
              placeholder="Enter your email address"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
            <TouchableOpacity 
              style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]} 
              onPress={handleEarlyAccess}
              disabled={isSubmitting}
            >
              <Text style={styles.submitButtonText}>
                {isSubmitting ? 'Joining...' : 'Join Now'}
              </Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.privacyText}>
            🔒 No spam. Unsubscribe anytime. Your privacy is our priority.
          </Text>
        </View>
      </View>

      {/* Features Section */}
      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>Why Choose LearnOnTheGo?</Text>
        
        <View style={styles.featureGrid}>
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>⚡</Text>
            <Text style={styles.featureTitle}>Quick Generation</Text>
            <Text style={styles.featureDescription}>
              Create audio lectures in under 30 seconds. Just enter a topic and duration.
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>📱</Text>
            <Text style={styles.featureTitle}>Learn Anywhere</Text>
            <Text style={styles.featureDescription}>
              Perfect for commutes, workouts, walks, or any time you want to learn hands-free.
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>🎯</Text>
            <Text style={styles.featureTitle}>Personalized Content</Text>
            <Text style={styles.featureDescription}>
              Choose difficulty level, duration, and voice. From PDFs or custom topics.
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>🔐</Text>
            <Text style={styles.featureTitle}>Your API Keys</Text>
            <Text style={styles.featureDescription}>
              Bring your own API keys. No monthly fees. Complete control over your costs.
            </Text>
          </View>
        </View>
      </View>

      {/* How It Works */}
      <View style={styles.howItWorksSection}>
        <Text style={styles.sectionTitle}>How It Works</Text>
        
        <View style={styles.stepContainer}>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>1</Text>
            </View>
            <Text style={styles.stepText}>Enter a topic or upload a PDF document</Text>
          </View>
          
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>2</Text>
            </View>
            <Text style={styles.stepText}>Choose duration, difficulty, and voice preference</Text>
          </View>
          
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>3</Text>
            </View>
            <Text style={styles.stepText}>Get your personalized audio lecture in seconds</Text>
          </View>
        </View>
      </View>

      {/* Use Cases */}
      <View style={styles.useCasesSection}>
        <Text style={styles.sectionTitle}>Perfect For</Text>
        
        <View style={styles.useCaseGrid}>
          <Text style={styles.useCase}>🚶 Walking & Exercise</Text>
          <Text style={styles.useCase}>🚗 Commuting</Text>
          <Text style={styles.useCase}>📚 Research Papers</Text>
          <Text style={styles.useCase}>💼 Professional Development</Text>
          <Text style={styles.useCase}>🎓 Student Learning</Text>
          <Text style={styles.useCase}>♿ Accessibility</Text>
        </View>
      </View>

      {/* Final CTA */}
      <View style={styles.finalCtaSection}>
        <Text style={styles.finalCtaTitle}>Ready to Transform Your Learning?</Text>
        <Text style={styles.finalCtaDescription}>
          Join thousands of learners who are already using AI to create personalized audio content.
        </Text>
        <TouchableOpacity style={styles.finalCtaButton} onPress={handleEarlyAccess}>
          <Text style={styles.finalCtaButtonText}>Get Early Access - Free</Text>
        </TouchableOpacity>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          LearnOnTheGo • Built with ❤️ for lifelong learners
        </Text>
        <Text style={styles.footerSubtext}>
          Phase 2d: Full authentication system in development
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  contentContainer: {
    paddingBottom: 40,
  },
  
  // Hero Section
  heroSection: {
    paddingHorizontal: 20,
    paddingVertical: 60,
    alignItems: 'center',
    backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    minHeight: 500,
  },
  heroEmoji: {
    fontSize: 64,
    marginBottom: 16,
  },
  heroTitle: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  heroSubtitle: {
    fontSize: 20,
    color: '#6366f1',
    marginBottom: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  heroDescription: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 40,
    maxWidth: 500,
    paddingHorizontal: 20,
  },
  
  // Early Access Section
  earlyAccessContainer: {
    backgroundColor: '#ffffff',
    padding: 32,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
    width: '100%',
    maxWidth: 400,
  },
  earlyAccessTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 20,
  },
  emailContainer: {
    marginBottom: 16,
  },
  emailInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    marginBottom: 12,
    backgroundColor: '#f9fafb',
  },
  submitButton: {
    backgroundColor: '#6366f1',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  privacyText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  
  // Features Section
  featuresSection: {
    padding: 40,
    backgroundColor: '#f8fafc',
  },
  sectionTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 40,
  },
  featureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 20,
  },
  featureCard: {
    backgroundColor: '#ffffff',
    padding: 24,
    borderRadius: 12,
    width: '48%',
    minWidth: 280,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 4,
  },
  featureIcon: {
    fontSize: 32,
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  
  // How It Works
  howItWorksSection: {
    padding: 40,
  },
  stepContainer: {
    gap: 24,
  },
  step: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  stepNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#6366f1',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumberText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  stepText: {
    fontSize: 16,
    color: '#374151',
    flex: 1,
  },
  
  // Use Cases
  useCasesSection: {
    padding: 40,
    backgroundColor: '#f8fafc',
  },
  useCaseGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  useCase: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    fontSize: 14,
    color: '#374151',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  
  // Final CTA
  finalCtaSection: {
    padding: 40,
    alignItems: 'center',
    backgroundColor: '#1f2937',
  },
  finalCtaTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 16,
  },
  finalCtaDescription: {
    fontSize: 16,
    color: '#d1d5db',
    textAlign: 'center',
    marginBottom: 32,
    maxWidth: 400,
  },
  finalCtaButton: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
  },
  finalCtaButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  
  // Footer
  footer: {
    padding: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  footerText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  footerSubtext: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 4,
  },
});

export default App;

export default App;
