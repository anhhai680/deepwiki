# DeepWiki Testing Framework

This directory contains the comprehensive test suite for the DeepWiki project, covering backend functionality, API endpoints, components, and utilities. The testing framework ensures code quality, reliability, and maintainability.

## 🧪 Test Structure

```
test/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── test_api.py                    # API endpoint testing
├── test_chat_pipeline.py          # Chat pipeline functionality
├── test_chat_service.py           # Chat service layer
├── test_core_infrastructure.py    # Core system infrastructure
├── test_embedder_components.py    # Embedding and vector operations
├── test_extract_repo_name.py      # Repository name extraction
├── test_generator_components.py   # AI text generation components
├── test_project_service.py        # Project management service
├── test_rag_pipeline.py           # RAG pipeline functionality
├── test_retriever_components.py   # Retrieval system components
├── test_utils.py                  # Utility functions
└── test_vector_operations.py      # Vector database operations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pytest framework
- Required test dependencies
- Backend environment setup

### Installation

```bash
# Install test dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Or install from project root
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest test/

# Run with coverage
python -m pytest test/ --cov=backend --cov-report=html

# Run specific test file
python -m pytest test/test_api.py

# Run specific test function
python -m pytest test/test_api.py::test_root_endpoint

# Run with verbose output
python -m pytest test/ -v

# Run tests in parallel
python -m pytest test/ -n auto
```

### Using Test Scripts

```bash
# Make scripts executable
chmod +x tools/run-tests.sh

# Run complete test suite
./tools/run-tests.sh

# Run with specific options
./tools/run-tests.sh --verbose --coverage --parallel
```

## 📋 Test Categories

### 1. API Testing (`test_api.py`)
Tests for FastAPI endpoints and HTTP responses:
- **Root Endpoints**: Basic API functionality
- **Health Checks**: Service health monitoring
- **Error Handling**: Proper error responses
- **CORS Configuration**: Cross-origin request handling
- **Response Formats**: JSON response validation

### 2. Pipeline Testing
Tests for core processing pipelines:

#### Chat Pipeline (`test_chat_pipeline.py`)
- Message processing and validation
- AI provider integration
- Response streaming
- Context management
- Error handling

#### RAG Pipeline (`test_rag_pipeline.py`)
- Retrieval augmented generation
- Document processing
- Vector search operations
- Context building
- Response generation

### 3. Component Testing
Tests for individual system components:

#### Embedder Components (`test_embedder_components.py`)
- Text embedding generation
- Vector storage operations
- Model provider integration
- Configuration management
- Performance optimization

#### Generator Components (`test_generator_components.py`)
- AI text generation
- Model selection
- Provider switching
- Response processing
- Error handling

#### Retriever Components (`test_retriever_components.py`)
- Document retrieval
- Similarity search
- Context building
- Result ranking
- Performance metrics

### 4. Service Layer Testing
Tests for business logic services:

#### Chat Service (`test_chat_service.py`)
- Conversation management
- Message history
- Context persistence
- Service integration
- Error handling

#### Project Service (`test_project_service.py`)
- Project lifecycle management
- Repository processing
- Cache management
- Data persistence
- Cleanup operations

### 5. Infrastructure Testing
Tests for core system infrastructure:

#### Core Infrastructure (`test_core_infrastructure.py`)
- System initialization
- Configuration loading
- Dependency injection
- Error handling
- Logging setup

#### Vector Operations (`test_vector_operations.py`)
- Vector database operations
- Index management
- Search algorithms
- Performance optimization
- Data consistency

### 6. Utility Testing (`test_utils.py`)
Tests for utility functions:
- Text processing utilities
- File operations
- Validation functions
- Configuration utilities
- Response processing

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
```

### Test Fixtures (`conftest.py`)

Common test fixtures and setup:

```python
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app

@pytest.fixture
def client():
    """Create test client for API testing."""
    app = create_app()
    return TestClient(app)

@pytest.fixture
def sample_repo_data():
    """Sample repository data for testing."""
    return {
        "url": "https://github.com/testuser/testrepo",
        "type": "github",
        "access_token": "test_token_123"
    }

@pytest.fixture
def mock_ai_response():
    """Mock AI response for testing."""
    return {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"total_tokens": 10}
    }
```

## 📊 Test Coverage

### Coverage Goals
- **Overall Coverage**: >90%
- **Critical Paths**: 100%
- **API Endpoints**: 100%
- **Core Components**: >95%
- **Utility Functions**: >90%

### Coverage Reports

```bash
# Generate HTML coverage report
python -m pytest test/ --cov=backend --cov-report=html

# Generate XML coverage report (for CI/CD)
python -m pytest test/ --cov=backend --cov-report=xml

# Generate terminal coverage report
python -m pytest test/ --cov=backend --cov-report=term-missing
```

### Coverage Configuration

```ini
[coverage:run]
source = backend
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */migrations/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

## 🎯 Testing Strategies

### 1. Unit Testing
- **Isolation**: Test individual functions and methods
- **Mocking**: Use mocks for external dependencies
- **Fast Execution**: Quick feedback during development
- **Coverage**: Ensure all code paths are tested

### 2. Integration Testing
- **Component Interaction**: Test component integration
- **API Endpoints**: Test complete request-response cycles
- **Database Operations**: Test data persistence and retrieval
- **External Services**: Test third-party service integration

### 3. End-to-End Testing
- **User Workflows**: Test complete user journeys
- **System Integration**: Test full system functionality
- **Performance**: Test system performance under load
- **Error Scenarios**: Test error handling and recovery

### 4. Performance Testing
- **Load Testing**: Test system under various loads
- **Stress Testing**: Test system limits and failure modes
- **Memory Testing**: Test memory usage and leaks
- **Response Time**: Test API response times

## 🔍 Test Utilities

### Test Helpers

```python
# Test data generators
def create_test_repository():
    """Create test repository data."""
    return {
        "name": "test-repo",
        "url": "https://github.com/test/test-repo",
        "type": "github"
    }

# Mock utilities
def mock_ai_provider():
    """Mock AI provider responses."""
    return Mock(spec=AIProvider)

# Assertion helpers
def assert_valid_response(response):
    """Assert response is valid."""
    assert response.status_code == 200
    assert "data" in response.json()
```

### Test Data Management

```python
# Test database setup
@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    # Setup test database
    yield test_db
    # Cleanup test database

# Test file management
@pytest.fixture
def temp_files():
    """Create temporary test files."""
    files = []
    # Create test files
    yield files
    # Cleanup test files
```

## 🚨 Error Testing

### Expected Errors
- **Validation Errors**: Invalid input data
- **Authentication Errors**: Missing or invalid tokens
- **Rate Limiting**: API rate limit exceeded
- **Service Errors**: External service failures
- **System Errors**: Internal system failures

### Error Response Testing

```python
def test_invalid_repository_url(client):
    """Test invalid repository URL handling."""
    response = client.post("/api/v1/wiki/generate", json={
        "repo_url": "invalid-url"
    })
    
    assert response.status_code == 400
    assert "error" in response.json()
    assert "Invalid repository URL" in response.json()["error"]
```

## 📈 Performance Testing

### Load Testing

```python
import asyncio
import time

async def test_api_performance(client, num_requests=100):
    """Test API performance under load."""
    start_time = time.time()
    
    tasks = []
    for _ in range(num_requests):
        task = client.get("/health")
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Calculate performance metrics
    total_time = end_time - start_time
    avg_response_time = total_time / num_requests
    
    assert avg_response_time < 0.1  # 100ms threshold
    assert all(r.status_code == 200 for r in responses)
```

### Memory Testing

```python
import psutil
import gc

def test_memory_usage():
    """Test memory usage during operations."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operation
    perform_operation()
    
    # Force garbage collection
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert memory increase is reasonable
    assert memory_increase < 50 * 1024 * 1024  # 50MB threshold
```

## 🔄 Continuous Integration

### GitHub Actions Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          python -m pytest test/ --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## 📚 Best Practices

### Test Organization
1. **Group Related Tests**: Organize tests by functionality
2. **Use Descriptive Names**: Clear test function names
3. **Follow AAA Pattern**: Arrange, Act, Assert
4. **Keep Tests Independent**: No test dependencies
5. **Clean Up Resources**: Proper fixture cleanup

### Test Data Management
1. **Use Fixtures**: Reusable test data setup
2. **Minimize Test Data**: Use minimal required data
3. **Clean Up**: Ensure proper cleanup after tests
4. **Isolate Data**: Prevent test data interference
5. **Use Factories**: Generate test data programmatically

### Assertion Best Practices
1. **Specific Assertions**: Use specific assertion methods
2. **Clear Messages**: Provide clear failure messages
3. **One Assertion Per Test**: Focus on single behavior
4. **Test Edge Cases**: Include boundary conditions
5. **Validate Structure**: Check response structure and content

## 🔗 Related Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Backend Documentation](../backend/README.md)
- [Development Tools](../tools/README.md)
- [Main Project README](../README.md)

## 🤝 Contributing

### Adding New Tests
1. **Identify Test Need**: Determine what needs testing
2. **Write Test Cases**: Create comprehensive test coverage
3. **Follow Patterns**: Use established testing patterns
4. **Update Documentation**: Document new test functionality
5. **Maintain Coverage**: Ensure adequate test coverage

### Test Standards
- **Coverage**: Maintain >90% code coverage
- **Performance**: Tests should run quickly
- **Reliability**: Tests should be deterministic
- **Maintainability**: Tests should be easy to understand
- **Documentation**: Clear test purpose and setup

## 📄 License

This testing framework is part of the DeepWiki project and follows the same MIT license terms.
