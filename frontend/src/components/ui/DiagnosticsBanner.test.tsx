import React from 'react';
import { render } from '@testing-library/react-native';

import DiagnosticsBanner from './DiagnosticsBanner';

const flattenStyle = (style: unknown): Record<string, unknown> => {
  if (!style) return {};
  if (Array.isArray(style)) {
    return style.reduce<Record<string, unknown>>((acc, entry) => ({
      ...acc,
      ...(typeof entry === 'object' && entry ? entry : {}),
    }), {});
  }
  if (typeof style === 'object') {
    return style as Record<string, unknown>;
  }
  return {};
};

describe('DiagnosticsBanner tone mapping', () => {
  it('uses ready tone styling for ready outcome', () => {
    const { getByTestId } = render(
      <DiagnosticsBanner
        testID="ready-banner"
        status="ready"
        code="ready"
        message="Reachable and ready"
        guidance="URL generation remains disabled in this slice."
      />
    );

    const bannerStyle = flattenStyle(getByTestId('ready-banner').props.style);
    const codeStyle = flattenStyle(getByTestId('url-diagnostics-code').props.style);

    expect(bannerStyle.backgroundColor).toBe('#e8f1e8');
    expect(bannerStyle.borderColor).toBe('#8eaf96');
    expect(codeStyle.color).toBe('#1d5e3e');
  });

  it('uses non-ready error tone styling', () => {
    const { getByTestId } = render(
      <DiagnosticsBanner
        testID="error-banner"
        status="unsupported"
        code="unsupported"
        message="Source type unsupported"
        guidance="Use text or file mode for this slice."
      />
    );

    const bannerStyle = flattenStyle(getByTestId('error-banner').props.style);
    const codeStyle = flattenStyle(getByTestId('url-diagnostics-code').props.style);

    expect(bannerStyle.backgroundColor).toBe('#f8e7e3');
    expect(bannerStyle.borderColor).toBe('#c06b5d');
    expect(codeStyle.color).toBe('#7d2f22');
  });
});
