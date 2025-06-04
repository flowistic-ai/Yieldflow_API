# Dependency Management Guide

## Overview

This document outlines best practices for managing dependencies in the Yieldflow API to avoid version conflicts and ensure reproducible builds.

## Requirement Files Structure

We use multiple requirement files for different environments:

- `requirements.txt` - Base dependencies with flexible version ranges
- `requirements-prod.txt` - Production dependencies with exact versions
- `requirements-dev.txt` - Development dependencies including testing tools

## Installation Commands

### Development Environment
```bash
pip install -r requirements-dev.txt
```

### Production Environment
```bash
pip install -r requirements-prod.txt
```

### Base Installation Only
```bash
pip install -r requirements.txt
```

## Version Pinning Strategy

### 1. Exact Pinning (Production)
Use exact versions for production to ensure reproducible builds:
```
fastapi==0.104.1
pandas==2.1.4
```

### 2. Compatible Release (Development)
Use compatible release specifiers for development flexibility:
```
pandas>=2.1.0,<2.2.0
numpy>=1.24.0,<1.27.0
```

### 3. Minimum Version (Optional Dependencies)
For optional or flexible dependencies:
```
plotly>=5.17.0,<6.0.0
```

## Dependency Update Process

### 1. Regular Updates
- Review dependencies monthly
- Update non-breaking versions automatically
- Test major version updates in development first

### 2. Security Updates
- Monitor security advisories
- Update vulnerable packages immediately
- Use tools like `safety` for vulnerability scanning

### 3. Testing Updates
```bash
# Create virtual environment
python -m venv test_env
source test_env/bin/activate

# Install updated dependencies
pip install -r requirements.txt

# Run tests
pytest

# If tests pass, update requirements files
pip freeze > requirements-freeze.txt
```

## Avoiding Common Issues

### 1. Conflicting Dependencies
```bash
# Use pip-tools for dependency resolution
pip install pip-tools
pip-compile requirements.in --upgrade
```

### 2. Platform-Specific Issues
```bash
# Lock dependencies for specific platforms
pip freeze --all > requirements-$(python -c "import platform; print(platform.system().lower())").txt
```

### 3. Virtual Environment Best Practices
```bash
# Always use virtual environments
python -m venv yieldflow_env
source yieldflow_env/bin/activate  # Linux/Mac
# or
yieldflow_env\Scripts\activate  # Windows

# Upgrade pip first
pip install --upgrade pip
```

## Monitoring and Maintenance

### 1. Automated Tools
- **Dependabot**: Automated dependency updates
- **Safety**: Security vulnerability scanning
- **pip-audit**: Security auditing

### 2. Regular Checks
```bash
# Check for outdated packages
pip list --outdated

# Check for security vulnerabilities
safety check

# Check for unused dependencies
pip-autoremove --list
```

### 3. Documentation
- Always document why specific versions are pinned
- Keep changelog of dependency updates
- Document any known compatibility issues

## Emergency Procedures

### 1. Broken Dependency
```bash
# Rollback to last known working state
git checkout HEAD~1 requirements.txt
pip install -r requirements.txt

# Or pin to previous working version
pip install package_name==previous_version
```

### 2. Security Vulnerability
```bash
# Immediate update
pip install package_name --upgrade

# Test in isolation
python -c "import package_name; print('OK')"

# Update requirements file
pip freeze | grep package_name >> requirements.txt
```

## Best Practices Summary

1. **Use virtual environments** always
2. **Pin exact versions** for production
3. **Use ranges** for development flexibility
4. **Test updates** before deploying
5. **Monitor security** advisories
6. **Document changes** with reasoning
7. **Automate where possible** but verify manually
8. **Keep backups** of working dependency sets

## Tools and Commands

### Essential Tools
```bash
pip install pip-tools safety pip-autoremove
```

### Common Commands
```bash
# Generate locked requirements
pip-compile requirements.in

# Sync environment with requirements
pip-sync requirements.txt

# Check security
safety check

# Remove unused packages
pip-autoremove
```

This approach ensures stable, secure, and maintainable dependency management for the Yieldflow API. 