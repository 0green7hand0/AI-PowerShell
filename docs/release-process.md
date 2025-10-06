# Release Process Guide

This document describes the complete release process for AI PowerShell Assistant.

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] All documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] No critical bugs or security issues
- [ ] Performance benchmarks meet targets
- [ ] Docker images build successfully

### Release

- [ ] Create release branch
- [ ] Run release checks
- [ ] Build release artifacts
- [ ] Create and push Git tag
- [ ] Create GitHub Release
- [ ] Publish Docker images
- [ ] Update documentation links
- [ ] Announce release

### Post-Release

- [ ] Monitor for issues
- [ ] Update project board
- [ ] Plan next release
- [ ] Archive release artifacts

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (x.X.0): Backward-compatible new features
- **PATCH** (x.x.X): Backward-compatible bug fixes

Examples:
- `1.0.0` → `2.0.0`: Major architectural changes (breaking)
- `2.0.0` → `2.1.0`: New features (compatible)
- `2.1.0` → `2.1.1`: Bug fixes (compatible)

## Release Process

### 1. Prepare Release

#### Update Version Numbers

Update version in `pyproject.toml`:

```toml
[project]
name = "ai-powershell"
version = "2.0.0"  # Update this
```

Update version in code if needed:

```python
# src/__init__.py
__version__ = "2.0.0"
```

#### Update CHANGELOG.md

Add release notes to CHANGELOG.md:

```markdown
## [2.0.0] - 2025-01-20

### Added
- New modular architecture
- Complete interface definitions
- Enhanced security features

### Changed
- Refactored all modules
- Improved performance by 40%

### Fixed
- PowerShell detection issues
- Chinese encoding problems

### Breaking Changes
- New import paths
- Configuration file location changed
```

#### Update Documentation

Ensure all documentation reflects the new version:

```bash
# Update README.md
# Update docs/architecture.md
# Update docs/developer-guide.md
# Update installation guides
```

### 2. Run Release Checks

Run comprehensive checks:

```bash
# Using Makefile
make release-check

# Or manually
make test
make quality
make coverage
make docker-build
make docker-test
```

Verify all checks pass:

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Code coverage > 80%
- ✅ No linting errors
- ✅ Type checking passes
- ✅ Docker image builds
- ✅ Docker image runs correctly

### 3. Create Release Branch

```bash
# Create release branch
git checkout -b release/v2.0.0

# Commit version updates
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v2.0.0"

# Push release branch
git push origin release/v2.0.0
```

### 4. Build Release Artifacts

#### Python Package

```bash
# Build distribution packages
python -m build

# Verify packages
ls -lh dist/
# Should see:
# - ai_powershell-2.0.0-py3-none-any.whl
# - ai_powershell-2.0.0.tar.gz

# Test installation
pip install dist/ai_powershell-2.0.0-py3-none-any.whl
```

#### Docker Images

```bash
# Build Docker images
docker build -t ai-powershell:2.0.0 .
docker tag ai-powershell:2.0.0 ai-powershell:latest

# Test Docker image
docker run --rm ai-powershell:2.0.0 python -c "from src.main import PowerShellAssistant; print('OK')"
```

### 5. Create Git Tag

```bash
# Create annotated tag
git tag -a v2.0.0 -m "Release version 2.0.0

Major architectural overhaul with modular design.

Highlights:
- Complete modular architecture
- Interface-driven design
- Enhanced security features
- Improved performance (40% faster)
- Better documentation

See RELEASE_NOTES.md for full details."

# Verify tag
git tag -v v2.0.0

# Push tag
git push origin v2.0.0
```

### 6. Create GitHub Release

#### Using GitHub CLI

```bash
# Create release with notes
gh release create v2.0.0 \
  --title "AI PowerShell 2.0.0 - Modular Architecture" \
  --notes-file RELEASE_NOTES.md \
  dist/ai_powershell-2.0.0-py3-none-any.whl \
  dist/ai_powershell-2.0.0.tar.gz

# Mark as latest
gh release edit v2.0.0 --latest
```

#### Using GitHub Web Interface

1. Go to: https://github.com/0green7hand0/AI-PowerShell/releases/new
2. Select tag: `v2.0.0`
3. Release title: `AI PowerShell 2.0.0 - Modular Architecture`
4. Description: Copy from `RELEASE_NOTES.md`
5. Attach files:
   - `ai_powershell-2.0.0-py3-none-any.whl`
   - `ai_powershell-2.0.0.tar.gz`
6. Check "Set as the latest release"
7. Click "Publish release"

### 7. Publish Docker Images

#### GitHub Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag images
docker tag ai-powershell:2.0.0 ghcr.io/0green7hand0/ai-powershell:2.0.0
docker tag ai-powershell:2.0.0 ghcr.io/0green7hand0/ai-powershell:latest

# Push images
docker push ghcr.io/0green7hand0/ai-powershell:2.0.0
docker push ghcr.io/0green7hand0/ai-powershell:latest
```

#### Docker Hub (Optional)

```bash
# Login to Docker Hub
docker login

# Tag images
docker tag ai-powershell:2.0.0 0green7hand0/ai-powershell:2.0.0
docker tag ai-powershell:2.0.0 0green7hand0/ai-powershell:latest

# Push images
docker push 0green7hand0/ai-powershell:2.0.0
docker push 0green7hand0/ai-powershell:latest
```

### 8. Publish to PyPI (Optional)

```bash
# Install twine
pip install twine

# Check packages
twine check dist/*

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ai-powershell

# If successful, upload to PyPI
twine upload dist/*
```

### 9. Update Documentation

Update documentation links and references:

```bash
# Update README.md badges
# Update installation instructions
# Update Docker image references
# Update version numbers in examples
```

Commit and push documentation updates:

```bash
git add README.md docs/
git commit -m "docs: update for v2.0.0 release"
git push origin main
```

### 10. Merge Release Branch

```bash
# Merge release branch to main
git checkout main
git merge release/v2.0.0
git push origin main

# Delete release branch
git branch -d release/v2.0.0
git push origin --delete release/v2.0.0
```

### 11. Announce Release

#### GitHub Discussions

Create announcement in GitHub Discussions:

```markdown
# 🎉 AI PowerShell 2.0.0 Released!

We're excited to announce the release of AI PowerShell 2.0.0!

## Highlights

- Complete modular architecture
- 40% performance improvement
- Enhanced security features
- Better documentation

## Download

- GitHub Release: https://github.com/0green7hand0/AI-PowerShell/releases/tag/v2.0.0
- Docker: `docker pull ghcr.io/0green7hand0/ai-powershell:2.0.0`
- PyPI: `pip install ai-powershell==2.0.0`

## Documentation

- Release Notes: https://github.com/0green7hand0/AI-PowerShell/blob/main/RELEASE_NOTES.md
- Migration Guide: https://github.com/0green7hand0/AI-PowerShell/blob/main/RELEASE_NOTES.md#migration-guide

Thank you to all contributors!
```

#### Social Media (Optional)

- Twitter/X
- LinkedIn
- Reddit (r/PowerShell, r/Python)
- Dev.to
- Hacker News

## Hotfix Process

For critical bugs in production:

### 1. Create Hotfix Branch

```bash
# Create from main/release tag
git checkout -b hotfix/v2.0.1 v2.0.0

# Fix the issue
# ... make changes ...

# Commit fix
git commit -m "fix: critical security issue"
```

### 2. Update Version

```bash
# Update to patch version
# pyproject.toml: version = "2.0.1"

# Update CHANGELOG.md
## [2.0.1] - 2025-01-21

### Fixed
- Critical security vulnerability in command validation
```

### 3. Test and Release

```bash
# Run tests
make test

# Create tag
git tag -a v2.0.1 -m "Hotfix release v2.0.1"

# Push
git push origin hotfix/v2.0.1
git push origin v2.0.1

# Create GitHub release
gh release create v2.0.1 --title "Hotfix v2.0.1" --notes "Critical security fix"

# Merge to main
git checkout main
git merge hotfix/v2.0.1
git push origin main
```

## Rollback Process

If a release has critical issues:

### 1. Identify Issue

- Monitor GitHub Issues
- Check error reports
- Review metrics

### 2. Decide on Action

- **Minor issue**: Create hotfix
- **Major issue**: Rollback release

### 3. Rollback Steps

```bash
# Mark release as pre-release
gh release edit v2.0.0 --prerelease

# Add warning to release notes
gh release edit v2.0.0 --notes "⚠️ WARNING: This release has been rolled back due to critical issues. Please use v1.2.0 instead."

# Revert Docker images
docker tag ghcr.io/0green7hand0/ai-powershell:1.2.0 ghcr.io/0green7hand0/ai-powershell:latest
docker push ghcr.io/0green7hand0/ai-powershell:latest

# Announce rollback
# Post in GitHub Discussions
# Update documentation
```

## Automation

### GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          body_path: RELEASE_NOTES.md
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/0green7hand0/ai-powershell:${{ github.ref_name }}
            ghcr.io/0green7hand0/ai-powershell:latest
```

## Best Practices

1. **Test Thoroughly**: Never skip testing
2. **Document Everything**: Update all documentation
3. **Communicate Clearly**: Announce changes prominently
4. **Version Carefully**: Follow semantic versioning
5. **Backup First**: Tag before making changes
6. **Monitor After**: Watch for issues post-release
7. **Plan Ahead**: Schedule releases in advance
8. **Automate**: Use CI/CD for consistency

## Troubleshooting

### Build Fails

```bash
# Clean and rebuild
make clean
make release-build
```

### Tag Already Exists

```bash
# Delete local tag
git tag -d v2.0.0

# Delete remote tag
git push origin :refs/tags/v2.0.0

# Recreate tag
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0
```

### Docker Push Fails

```bash
# Re-login
docker logout ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Retry push
docker push ghcr.io/0green7hand0/ai-powershell:2.0.0
```

## References

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [Docker Hub](https://docs.docker.com/docker-hub/)

## Support

For questions about the release process:
- GitHub Discussions: https://github.com/0green7hand0/AI-PowerShell/discussions
- Email: contact@ai-powershell.dev
