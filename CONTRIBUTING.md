# Contributing to Buddhist Education System

Thank you for your interest in contributing to this project!

## 🌟 How to Contribute

### 1. Fork and Clone

```bash
git fork https://github.com/YOUR_USERNAME/buddhist-education-system
git clone https://github.com/YOUR_USERNAME/buddhist-education-system.git
cd buddhist-education-system
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow the existing code style
- Add tests if applicable
- Update documentation as needed

### 4. Test Your Changes

**For Ebook System:**
```bash
cd ebook
python test_*.py
```

**For LINE Bot:**
```bash
cd Line-bot-llm-mysql
npm test
npm run lint
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## 📋 Development Guidelines

### Code Style

**Python (Ebook System):**
- Follow PEP 8 style guide
- Use snake_case for variables and functions
- Add docstrings to functions and classes
- Keep functions focused and small

**TypeScript (LINE Bot):**
- Follow TypeScript best practices
- Use camelCase for variables and functions
- Use PascalCase for classes and interfaces
- Add JSDoc comments for public APIs
- Use proper type annotations

### Project Structure

- Keep ebook-related code in `/ebook/`
- Keep LINE bot code in `/Line-bot-llm-mysql/`
- Add feature specs to `.kiro/specs/`
- Update steering rules in `.kiro/steering/` if needed

### Documentation

- Update README files when adding features
- Add inline comments for complex logic
- Create feature documentation in `/docs/` for major features
- Keep CHANGELOG updated

### Testing

- Add unit tests for new functionality
- Ensure existing tests pass
- Test manually before submitting PR

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Description** - Clear description of the issue
2. **Steps to Reproduce** - How to reproduce the issue
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment** - OS, Python/Node version, etc.
6. **Logs** - Relevant error messages or logs

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Describe the feature clearly
3. Explain the use case
4. Provide examples if possible

## 🔒 Security

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. Email the maintainers directly
3. Provide details about the vulnerability
4. Wait for a response before disclosing

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect the project's purpose for Buddhist education

## 🙏 Thank You

Your contributions help improve Buddhist education resources. Thank you for your support!

---

**May your contributions bring benefit to all beings** 🙏
