# DeepWiki GitHub Workflows

This directory contains GitHub Actions workflows for the DeepWiki project.

## Workflows

### `deepwiki-ci.yml` - Core CI Pipeline

**Purpose**: Ensures the three main requirements are met:
1. ✅ **Coding syntax not failed** - Comprehensive syntax and code quality checks
2. ✅ **Build docker with docker-compose.yml successfully** - Docker build and compose validation
3. ✅ **All test cases in test/ folder MUST be passed** - Complete test execution

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

**Jobs**:
- **syntax-check**: Python and TypeScript syntax validation, code formatting, and linting
- **docker-build**: Docker image build, compose validation, and container startup testing
- **test-execution**: Runs all Python tests with coverage reporting
- **final-check**: Aggregates results and provides status summary

**Why This Workflow?**
This workflow is optimized for your core requirements and avoids duplication. It provides:
- Focused testing on your three main requirements
- Faster execution time
- Clear pass/fail indicators
- Efficient resource usage

## Configuration Files

### `.flake8`
Python code quality configuration for flake8 linting.

### `pyproject.toml`
Contains tool configurations for:
- `black` - Python code formatter
- `isort` - Python import sorter
- `pytest` - Python testing framework

## Usage

### Automatic Execution
Workflows run automatically on:
- Every push to protected branches
- Every pull request
- Manual trigger via GitHub Actions tab

### Manual Execution
1. Go to GitHub Actions tab in your repository
2. Select the workflow you want to run
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

### Local Testing
Before pushing, you can run checks locally to match the CI workflow:

```bash
# 1. Coding syntax check (matches syntax-check job)
pip install flake8 black isort
python -m py_compile backend/main.py
python -m py_compile backend/app.py
flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
black --check backend/
isort --check-only backend/
npm run lint
npx eslint src/ --ext .ts,.tsx,.js,.jsx
npx tsc --noEmit

# 2. Docker build test (matches docker-build job)
docker build -t deepwiki:test .
docker-compose -f docker-compose.yml config
docker-compose -f docker-compose.yml build

# 3. Test execution (matches test-execution job)
cd backend
python -m pytest test/ -v --tb=short
python -m pytest test/ --cov=. --cov-report=term-missing
```

## Requirements

- Python 3.12+
- Node.js 20+
- Docker and Docker Compose
- All dependencies specified in `requirements.txt` and `package.json`

## Troubleshooting

### Common Issues

1. **Docker Build Failures**
   - Check Dockerfile syntax
   - Verify all required files are present
   - Check resource limits in docker-compose.yml

2. **Test Failures**
   - Run tests locally to reproduce issues
   - Check test dependencies are installed
   - Verify test data and mocks are correct

3. **Syntax Check Failures**
   - Run `black` to auto-format code
   - Run `isort` to fix import ordering
   - Address flake8 warnings manually

### Getting Help

- Check workflow logs in GitHub Actions
- Review the specific job that failed
- Run failing checks locally for debugging
- Check configuration files for syntax errors
