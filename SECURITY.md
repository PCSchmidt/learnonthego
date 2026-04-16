# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### For Critical Security Issues
- **DO NOT** create a public GitHub issue
- Email: [your-email@domain.com] with subject "SECURITY: LearnOnTheGo Vulnerability"
- Include detailed information about the vulnerability
- We will respond within 48 hours

### For Non-Critical Security Issues
- Create a private security advisory on GitHub
- Use the "Report a vulnerability" button in the Security tab

## Security Measures

### Data Protection
- **API Keys**: Encrypted with AES-256 before database storage
- **Passwords**: Hashed with bcrypt (cost factor 12)
- **JWT Tokens**: Stored in secure device storage (Keychain/Keystore)
- **PDF Files**: Automatically deleted after processing (max 24 hours)

### Input Validation
- **PDF Upload**: File type validation, size limits (50MB), malware scanning
- **Text Input**: SQL injection prevention, XSS protection
- **API Endpoints**: Rate limiting, authentication validation

### Infrastructure Security
- **HTTPS Only**: All communications encrypted in transit
- **Environment Variables**: Secrets stored in Railway/Vercel secure environment
- **Database**: PostgreSQL with connection encryption
- **File Storage**: Cloudinary with secure upload policies

### Authentication & Authorization
- **JWT Tokens**: Short expiration (30 minutes) with refresh token mechanism
- **Rate Limiting**: 
  - Login attempts: 5 attempts per 15 minutes
  - Lecture generation: 10 per hour per user
  - PDF uploads: 5 per hour per user
- **Session Management**: Secure token storage and validation

## Security Best Practices for Contributors

### Code Security
- Never commit API keys, passwords, or secrets
- Use environment variables for all configuration
- Validate all user inputs
- Implement proper error handling (don't expose system information)
- Use parameterized queries to prevent SQL injection

### Dependency Security
- Regularly update dependencies
- Run `npm audit` and `pip audit` before commits
- Use Bandit for Python security scanning
- Monitor GitHub security advisories

### API Security
- Implement proper CORS policies
- Use HTTPS for all external API calls
- Validate API responses before processing
- Implement timeout mechanisms for external calls

## Vulnerability Response Process

1. **Report Received**: Acknowledge within 48 hours
2. **Assessment**: Evaluate severity and impact (1-7 days)
3. **Fix Development**: Develop and test fix (timeline depends on severity)
4. **Disclosure**: Coordinate responsible disclosure with reporter
5. **Release**: Deploy fix and notify users
6. **Recognition**: Credit reporter (if desired) in security advisories

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1) and communicated through:
- GitHub Security Advisories
- Release notes
- Email notifications to registered users (when available)

## Scope

This security policy applies to:
- Main application code (backend and frontend)
- Infrastructure configuration
- Dependencies and third-party integrations
- User data handling and storage

Out of scope:
- Third-party services (OpenRouter, ElevenLabs, etc.)
- User's own API keys and accounts
- Social engineering attacks
- Physical security

## Contact

For security-related questions or concerns:
- Email: [your-email@domain.com]
- GitHub: Create a private security advisory
- Response time: Within 48 hours for critical issues

Thank you for helping keep LearnOnTheGo secure!
