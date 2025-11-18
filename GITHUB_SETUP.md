# GitHub Setup Guide

## 📤 Uploading to GitHub

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the "+" icon → "New repository"
3. Fill in repository details:
   - **Name**: `buddhist-education-system`
   - **Description**: Buddhist Education System - Ebook Summary & LINE Bot
   - **Visibility**: Public or Private
   - **DO NOT** initialize with README (we already have one)
4. Click "Create repository"

### Step 2: Connect Local Repository

```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/buddhist-education-system.git

# Verify remote
git remote -v
```

### Step 3: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### Alternative: Using GitHub CLI

```bash
# Install GitHub CLI (if not installed)
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Login
gh auth login

# Create and push repository
gh repo create buddhist-education-system --public --source=. --remote=origin --push
```

## 🔐 Setting Up Secrets

### For GitHub Actions

1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add the following secrets:

**LINE Bot Secrets:**
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `GEMINI_API_KEY`
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

**Cloud Deployment Secrets:**
- `GCP_PROJECT_ID` (for Google Cloud)
- `GCP_SA_KEY` (Service Account JSON)
- `VERCEL_TOKEN` (for Vercel)

## 📋 Repository Settings

### Branch Protection

1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

### Collaborators

1. Go to Settings → Collaborators
2. Add team members with appropriate permissions

### Topics

Add relevant topics to help others discover your project:
- `buddhist-education`
- `line-bot`
- `gemini-ai`
- `python`
- `typescript`
- `web-scraping`
- `automation`

## 📝 Repository Structure

Your GitHub repository will look like this:

```
buddhist-education-system/
├── .github/
│   └── workflows/          # CI/CD workflows (optional)
├── .kiro/                  # Kiro IDE configuration
├── ebook/                  # Python ebook system
├── Line-bot-llm-mysql/    # TypeScript LINE bot
├── docs/                   # Documentation
├── .gitignore
├── README.md
├── QUICK_START.md
├── PROJECT_STRUCTURE.md
├── CONTRIBUTING.md
├── DEPLOYMENT.md
├── LICENSE
└── GITHUB_SETUP.md
```

## 🏷️ Creating Releases

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

### Creating a Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

Or use GitHub UI:
1. Go to Releases → Draft a new release
2. Choose a tag (e.g., `v1.0.0`)
3. Write release notes
4. Attach binaries if needed
5. Publish release

## 📊 GitHub Features to Enable

### Issues

Enable issue templates:

Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug Report
about: Report a bug
---

**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior.

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Windows 10]
- Python/Node version:
- Browser (if applicable):
```

### Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
```

### GitHub Pages (Optional)

Host documentation:
1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: `main` → `/docs`
4. Save

## 🔄 Keeping Repository Updated

### Regular Maintenance

```bash
# Update dependencies
cd ebook && pip install -U -r requirements.txt
cd Line-bot-llm-mysql && npm update

# Commit updates
git add .
git commit -m "chore: update dependencies"
git push
```

### Syncing Forks

If others fork your repository:
```bash
# Add upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/buddhist-education-system.git

# Fetch and merge
git fetch upstream
git merge upstream/main
```

## 📢 Promoting Your Repository

### README Badges

Add badges to README.md:

```markdown
![License](https://img.shields.io/github/license/YOUR_USERNAME/buddhist-education-system)
![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/buddhist-education-system)
![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/buddhist-education-system)
```

### Social Media

Share your project:
- Twitter/X with hashtags: #OpenSource #BuddhistEducation #AI
- LinkedIn post
- Reddit (r/opensource, r/Buddhism)
- Dev.to article

## 🛡️ Security

### Enable Security Features

1. **Dependabot**
   - Settings → Security → Dependabot
   - Enable Dependabot alerts
   - Enable Dependabot security updates

2. **Code Scanning**
   - Settings → Security → Code scanning
   - Set up CodeQL analysis

3. **Secret Scanning**
   - Automatically enabled for public repos
   - Alerts you if secrets are committed

## 📞 Support

### GitHub Discussions

Enable Discussions for community support:
1. Settings → Features → Discussions
2. Create categories:
   - Q&A
   - Ideas
   - Show and tell
   - General

## ✅ Checklist

Before making repository public:

- [ ] Remove all sensitive data
- [ ] Update README with accurate information
- [ ] Add LICENSE file
- [ ] Create .gitignore
- [ ] Add CONTRIBUTING.md
- [ ] Test clone and setup on fresh machine
- [ ] Add repository description and topics
- [ ] Enable security features
- [ ] Create initial release

---

**Your repository is now ready for the world!** 🌍
