# Contributing to LearnOnTheGo

Thank you for your interest in contributing to LearnOnTheGo! This document provides guidelines and information for contributors.

## 🚀 Getting Started

1. **Fork the repository** and clone your fork
2. **Read the documentation**:
   - [README.md](README.md) - Project overview
   - [PROGRESS.md](PROGRESS.md) - Current execution status and priorities
   - [docs/archive/root-legacy-2026/PRD.md](docs/archive/root-legacy-2026/PRD.md) - Archived product requirements context
   - [GETTING_STARTED.md](GETTING_STARTED.md) - Development setup
   - [.github/copilot-instructions.md](.github/copilot-instructions.md) - Coding conventions

3. **Set up your development environment** following [GETTING_STARTED.md](GETTING_STARTED.md)

## 📋 Development Guidelines

### Code Standards
- **Backend**: Follow PEP 8, use Black for formatting, Flake8 for linting
- **Frontend**: Use Airbnb TypeScript style guide, ESLint for linting
- **Security**: Run Bandit security checks before submitting
- **Testing**: Maintain >80% test coverage for critical paths

### Commit Convention
Use conventional commits:
```
feat: add PDF processing pipeline
fix: resolve JWT token expiration issue
docs: update API documentation
test: add integration tests for lecture generation
refactor: optimize database queries
```

### Branch Naming
- `feature/feature-name` - New features
- `fix/bug-name` - Bug fixes
- `docs/update-name` - Documentation updates
- `refactor/component-name` - Code refactoring

## 🛠️ Development Process

### 1. Create a Feature Branch
```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 2. Development Workflow
```bash
# Backend development
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload

# Frontend development
cd frontend
npm start

# Run tests frequently
pytest --cov=.  # Backend
npm test       # Frontend
```

### 3. Code Quality Checks
```bash
# Backend
black .
flake8 .
bandit -r .
pytest --cov=. --cov-report=html

# Frontend
npm run lint
npm run type-check
npm test -- --coverage
```

### 4. Submit Pull Request
- Push your branch to your fork
- Create PR against `dev` branch (not `main`)
- Fill out the PR template completely
- Ensure all CI checks pass

## 🧪 Testing Requirements

### Backend Testing
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test API endpoints end-to-end
- **Security tests**: Validate authentication and input sanitization
- **Performance tests**: Ensure generation times meet requirements

### Frontend Testing
- **Component tests**: Test UI components in isolation
- **Integration tests**: Test user flows
- **Accessibility tests**: Ensure WCAG compliance
- **Cross-platform tests**: Test on iOS, Android, web

### Test Coverage Targets
- **Critical paths**: >90% (auth, lecture generation, PDF processing)
- **Overall coverage**: >80%
- **Security functions**: 100%

## 🔒 Security Guidelines

### API Key Handling
- Never commit API keys or secrets
- Use environment variables for all sensitive data
- Encrypt stored API keys with AES-256
- Validate all user inputs

### PDF Processing Security
- Reject scanned PDFs and executables
- Limit file size to 50MB
- Sanitize extracted text
- Delete temporary files within 24 hours

### Authentication Security
- Use bcrypt for password hashing
- Implement proper JWT token handling
- Add rate limiting for login attempts
- Validate all JWT tokens server-side

## 📚 Areas for Contribution

### High Priority
- **PDF processing improvements**: Better text extraction, OCR support
- **Audio optimization**: Better compression, quality controls
- **Mobile UX**: Improved React Native components
- **Performance**: Faster generation times, better caching

### Medium Priority
- **Accessibility**: WCAG 2.1 AA compliance improvements
- **Testing**: Additional test coverage
- **Documentation**: API docs, user guides
- **Monitoring**: Better error tracking and analytics

### Future Features
- **Multi-language support**: Spanish, French, Mandarin
- **Quiz mode**: Comprehension testing
- **Collaboration**: Team lecture sharing
- **Analytics**: Usage insights and recommendations

## 🐛 Bug Reports

When reporting bugs, please include:
- **Environment**: OS, Python version, Node.js version
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

Use this template:
```markdown
**Environment:**
- OS: Windows 11
- Python: 3.9.7
- Node.js: 18.17.0
- Browser: Chrome 119

**Steps to Reproduce:**
1. Upload a PDF file
2. Set duration to 30 minutes
3. Click "Generate Lecture"

**Expected:** Lecture generates successfully
**Actual:** Error message "PDF processing failed"

**Logs:**
[Include relevant logs here]
```

## 💡 Feature Requests

For feature requests, please:
1. Check existing issues and discussions first
2. Provide clear use case and rationale
3. Consider implementation complexity
4. Align with project goals (cost-conscious, mobile-first)

## 📖 Documentation

### API Documentation
- Use docstrings for all functions
- Follow OpenAPI/Swagger standards
- Include example requests/responses
- Document error codes and messages

### Code Documentation
- Comment complex logic
- Use type hints in Python
- Document environment variables
- Keep README.md updated

## 🎯 Performance Guidelines

### Backend Performance
- **Lecture generation**: <30s (text), <45s (PDF)
- **API response time**: <500ms for non-generation endpoints
- **Database queries**: Optimize with proper indexing
- **Memory usage**: Monitor for memory leaks

### Frontend Performance
- **App startup**: <3 seconds
- **Navigation**: <200ms between screens
- **Audio playback**: No buffering delays
- **Bundle size**: Keep minimal for mobile

## 🌍 Internationalization

When adding new features:
- Use translation keys, not hardcoded strings
- Consider right-to-left language support
- Test with different character sets
- Follow Unicode best practices

## 🤝 Code Review Process

### For Reviewers
- Check code quality and standards compliance
- Verify test coverage and security
- Test the feature locally
- Provide constructive feedback
- Approve only when ready for production

### For Contributors
- Respond to feedback promptly
- Make requested changes in new commits
- Don't force-push after review starts
- Update tests when changing functionality

## 📞 Getting Help

- **Development questions**: GitHub Discussions
- **Bug reports**: GitHub Issues
- **Security issues**: Email maintainer privately
- **General chat**: Project Discord (if available)

## 🙏 Recognition

Contributors will be:
- Listed in README.md acknowledgments
- Credited in release notes
- Invited to beta testing programs
- Considered for maintainer roles

Thank you for contributing to LearnOnTheGo! 🎧📚
