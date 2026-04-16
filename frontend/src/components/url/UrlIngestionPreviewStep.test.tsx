import React from 'react';
import { render } from '@testing-library/react-native';

import UrlIngestionPreviewStep from './UrlIngestionPreviewStep';

describe('UrlIngestionPreviewStep', () => {
  it('forwards diagnostics outcome, message, and guidance to DiagnosticsBanner', () => {
    const { getByTestId, getByText } = render(
      <UrlIngestionPreviewStep
        urlInput="https://example.com/source"
        onUrlChange={jest.fn()}
        onRunDiagnostics={jest.fn()}
        isDiagnosticsLoading={false}
        diagnostics={{
          success: true,
          schema: 'url-diagnostics-v1',
          contract_version: 'v1a',
          source_uri: 'https://example.com/source',
          source_class: 'web',
          outcome: 'unsupported',
          diagnostics: {
            code: 'unsupported',
            message: 'This source type is not supported for generation in this slice.',
            retryable: false,
          },
        }}
        diagnosticsGuidance="Use text or file mode until URL ingestion is enabled."
      />
    );

    expect(getByTestId('url-diagnostics-card')).toBeTruthy();
    expect(getByTestId('url-diagnostics-code').props.children).toBe('unsupported');
    expect(getByText('This source type is not supported for generation in this slice.')).toBeTruthy();
    expect(getByText('Use text or file mode until URL ingestion is enabled.')).toBeTruthy();
  });

  it('exposes accessible labels for URL input and diagnostics action', () => {
    const { getByLabelText } = render(
      <UrlIngestionPreviewStep
        urlInput=""
        onUrlChange={jest.fn()}
        onRunDiagnostics={jest.fn()}
        isDiagnosticsLoading={false}
        diagnostics={null}
      />
    );

    expect(getByLabelText('Source URL input')).toBeTruthy();
    expect(getByLabelText('Run URL diagnostics')).toBeTruthy();
  });
});
