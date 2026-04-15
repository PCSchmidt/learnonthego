module.exports = {
  root: true,
  extends: [
    '@react-native',
    'airbnb-typescript',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json',
  },
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'jsx-a11y',
    'import',
    'prettier'
  ],
  rules: {
    'prettier/prettier': 'warn',
    'react/jsx-filename-extension': [
      'error',
      { extensions: ['.tsx'] }
    ],
    'import/extensions': [
      'error',
      'ignorePackages',
      {
        ts: 'never',
        tsx: 'never',
      },
    ],
    'import/prefer-default-export': 'off',
    'react/prop-types': 'off',
    'react/require-default-props': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'jsx-a11y/accessible-emoji': 'off',
    'jsx-a11y/anchor-is-valid': 'off',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    'object-shorthand': 'error',
    'prefer-template': 'error',
  },
  settings: {
    'import/resolver': {
      typescript: {},
    },
    react: {
      version: 'detect',
    },
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.test.tsx'],
      env: {
        jest: true,
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
      },
    },
  ],
};
