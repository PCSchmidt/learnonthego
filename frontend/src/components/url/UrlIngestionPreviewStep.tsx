import React from 'react';
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

import DiagnosticsBanner from '../ui/DiagnosticsBanner';
import { UrlDiagnosticsResponse } from '../../services/lecture';

interface UrlIngestionPreviewStepProps {
  urlInput: string;
  onUrlChange: (value: string) => void;
  onRunDiagnostics: () => void;
  isDiagnosticsLoading: boolean;
  diagnostics: UrlDiagnosticsResponse | null;
  diagnosticsGuidance?: string;
  urlError?: string;
}

const UrlIngestionPreviewStep: React.FC<UrlIngestionPreviewStepProps> = ({
  urlInput,
  onUrlChange,
  onRunDiagnostics,
  isDiagnosticsLoading,
  diagnostics,
  diagnosticsGuidance,
  urlError,
}) => {
  return (
    <View style={styles.urlCard}>
      <Text style={styles.urlLabel}>Source URL</Text>
      <TextInput
        testID="url-input"
        style={styles.urlInput}
        value={urlInput}
        onChangeText={onUrlChange}
        placeholder="https://example.com/article"
        placeholderTextColor="#7f8492"
        autoCapitalize="none"
        autoCorrect={false}
      />
      <TouchableOpacity
        testID="run-url-diagnostics-button"
        style={[styles.urlDiagnosticsButton, isDiagnosticsLoading && styles.urlDiagnosticsButtonDisabled]}
        onPress={onRunDiagnostics}
        disabled={isDiagnosticsLoading}
      >
        <Text style={styles.urlDiagnosticsButtonText}>
          {isDiagnosticsLoading ? 'Running Diagnostics...' : 'Run URL Diagnostics'}
        </Text>
      </TouchableOpacity>

      {urlError ? <Text testID="url-error" style={styles.fieldError}>{urlError}</Text> : null}

      {diagnostics ? (
        <DiagnosticsBanner
          testID="url-diagnostics-card"
          status={diagnostics.outcome}
          code={diagnostics.outcome}
          message={diagnostics.diagnostics.message}
          guidance={diagnosticsGuidance || diagnostics.diagnostics.message}
        />
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  urlCard: {
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#b3aa95',
    backgroundColor: '#f9f5ea',
    padding: 12,
  },
  urlLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#3e3525',
    marginBottom: 8,
  },
  urlInput: {
    borderWidth: 1,
    borderColor: '#d8ccb6',
    borderRadius: 0,
    backgroundColor: '#ffffff',
    color: '#1f1f1f',
    paddingHorizontal: 10,
    paddingVertical: 10,
    marginBottom: 10,
  },
  urlDiagnosticsButton: {
    backgroundColor: '#3e3525',
    borderWidth: 1,
    borderColor: '#3e3525',
    alignItems: 'center',
    paddingVertical: 10,
  },
  urlDiagnosticsButtonDisabled: {
    opacity: 0.6,
  },
  urlDiagnosticsButtonText: {
    color: '#f6f1e5',
    fontWeight: '700',
    fontSize: 13,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  fieldError: {
    color: '#8f2d1f',
    fontSize: 13,
    marginTop: 8,
  },
});

export default UrlIngestionPreviewStep;
