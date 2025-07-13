import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const App: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎓 LearnOnTheGo</Text>
      <Text style={styles.subtitle}>Transform Learning Into Audio</Text>
      <Text style={styles.description}>
        Convert any topic or PDF into personalized audio lectures
      </Text>
      <View style={styles.comingSoon}>
        <Text style={styles.comingSoonText}>Coming Soon</Text>
        <Text style={styles.betaText}>Full authentication system in development</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#6366f1',
    marginBottom: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  description: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
    maxWidth: 400,
  },
  comingSoon: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  comingSoonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  betaText: {
    color: '#e0e7ff',
    fontSize: 12,
    marginTop: 4,
  },
});

export default App;
