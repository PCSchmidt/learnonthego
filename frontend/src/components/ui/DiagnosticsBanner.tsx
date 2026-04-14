import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export type DiagnosticsBannerStatus = 'unreachable' | 'unsupported' | 'no_transcript' | 'ready';

interface DiagnosticsBannerProps {
  status: DiagnosticsBannerStatus;
  code: string;
  message: string;
  guidance: string;
  testID?: string;
}

const DiagnosticsBanner: React.FC<DiagnosticsBannerProps> = ({
  status,
  code,
  message,
  guidance,
  testID,
}) => {
  const toneStyles = status === 'ready' ? styles.readyTone : styles.errorTone;
  const codeStyles = status === 'ready' ? styles.readyCode : styles.errorCode;

  return (
    <View testID={testID} style={[styles.base, toneStyles]}>
      <Text style={styles.title}>Diagnostics Result</Text>
      <Text testID="url-diagnostics-code" style={[styles.code, codeStyles]}>
        {code}
      </Text>
      <Text style={styles.message}>{message}</Text>
      <Text style={styles.guidance}>{guidance}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  base: {
    marginTop: 12,
    borderWidth: 1,
    padding: 12,
  },
  errorTone: {
    borderColor: '#c06b5d',
    backgroundColor: '#f8e7e3',
  },
  readyTone: {
    borderColor: '#8eaf96',
    backgroundColor: '#e8f1e8',
  },
  title: {
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    color: '#3e3525',
    marginBottom: 6,
    letterSpacing: 0.6,
  },
  code: {
    fontSize: 13,
    fontWeight: '800',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  errorCode: {
    color: '#7d2f22',
  },
  readyCode: {
    color: '#1d5e3e',
  },
  message: {
    fontSize: 13,
    color: '#3e3525',
    lineHeight: 18,
    marginBottom: 6,
  },
  guidance: {
    fontSize: 12,
    color: '#4f4635',
    lineHeight: 17,
  },
});

export default DiagnosticsBanner;
