# DeepWiki Development Tools

This directory contains development tools, utilities, and scripts that help maintain code quality, validate imports, and streamline the development workflow for the DeepWiki project.

## 🛠️ Available Tools

### Import Validation

#### `validate_imports.py`
A comprehensive import validation tool that checks for:
- Circular import dependencies
- Missing module imports
- Invalid import paths
- Package structure consistency

**Usage:**
```bash
# From project root
python tools/validate_imports.py

# With specific directory
python tools/validate_imports.py backend/

# With verbose output
python tools/validate_imports.py --verbose
```

**Features:**
- Detects circular import chains
- Validates relative vs absolute imports
- Checks package structure integrity
- Generates detailed import dependency reports
- Supports both backend and frontend validation

**Output:**
- Import dependency graph
- Circular import detection
- Missing module identification
- Import path validation results
- Recommendations for import optimization

### Development Scripts

#### `run-tests.sh`
Bash script for running the complete test suite:

```bash
# Make executable
chmod +x tools/run-tests.sh

# Run all tests
./tools/run-tests.sh

# Run with specific options
./tools/run-tests.sh --verbose --coverage
```

#### `run.sh`
Quick start script for development:

```bash
# Make executable
chmod +x tools/run.sh

# Start development environment
./tools/run.sh
```

## 🔧 Tool Development

### Adding New Tools

When creating new development tools:

1. **Follow Naming Convention**: Use descriptive names with appropriate extensions
2. **Include Documentation**: Add comprehensive help text and usage examples
3. **Error Handling**: Implement robust error handling and user feedback
4. **Configuration**: Support both command-line arguments and environment variables
5. **Testing**: Include tests for the tool itself

### Tool Structure

```python
#!/usr/bin/env python3
"""
Tool Name - Brief Description

Usage:
    python tools/tool_name.py [options]

Options:
    --help, -h          Show this help message
    --verbose, -v       Enable verbose output
    --config FILE       Configuration file path
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main tool execution."""
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    try:
        # Tool logic here
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 📋 Tool Categories

### Code Quality Tools
- **Import Validation**: Check import dependencies and structure
- **Linting**: Code style and quality enforcement
- **Type Checking**: Static type analysis
- **Security Scanning**: Vulnerability detection

### Development Workflow Tools
- **Test Runners**: Automated testing execution
- **Build Scripts**: Compilation and packaging
- **Deployment**: Automated deployment processes
- **Monitoring**: Development environment monitoring

### Utility Tools
- **Data Processing**: Scripts for data manipulation
- **File Management**: Bulk file operations
- **Configuration**: Environment and config management
- **Documentation**: Documentation generation and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required Python packages (see individual tool requirements)
- Appropriate permissions for file operations

### Installation

```bash
# Install tool dependencies
pip install -r tools/requirements.txt

# Or install specific tools
pip install -r tools/validate_imports-requirements.txt
```

### Basic Usage

```bash
# Validate all imports
python tools/validate_imports.py

# Run test suite
./tools/run-tests.sh

# Start development environment
./tools/run.sh
```

## 📊 Tool Output Examples

### Import Validation Report

```
DeepWiki Import Validation Report
================================

✅ All imports validated successfully
📊 Import Statistics:
   - Total modules: 45
   - Internal imports: 127
   - External imports: 23
   - Circular imports: 0

🔍 Detailed Analysis:
   - Backend modules: 32
   - Frontend modules: 13
   - Utility modules: 8

📁 Package Structure:
   backend/
   ├── api/v1/ ✅
   ├── components/ ✅
   ├── services/ ✅
   └── utils/ ✅

🎯 Recommendations:
   - Consider using relative imports for closely related modules
   - All circular imports resolved successfully
   - Import structure is clean and maintainable
```

### Test Execution Report

```
DeepWiki Test Suite Execution
============================

🧪 Running tests...
✅ test_api.py: 15/15 tests passed
✅ test_chat_pipeline.py: 8/8 tests passed
✅ test_core_infrastructure.py: 12/12 tests passed
✅ test_embedder_components.py: 6/6 tests passed
✅ test_generator_components.py: 9/9 tests passed
✅ test_project_service.py: 5/5 tests passed
✅ test_rag_pipeline.py: 11/11 tests passed
✅ test_retriever_components.py: 7/7 tests passed
✅ test_utils.py: 18/18 tests passed
✅ test_vector_operations.py: 4/4 tests passed

📊 Summary:
   - Total tests: 95
   - Passed: 95
   - Failed: 0
   - Skipped: 0
   - Coverage: 87.3%

🎉 All tests passed successfully!
```

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Make scripts executable
chmod +x tools/*.sh

# Check file permissions
ls -la tools/
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r tools/requirements.txt
```

#### Tool Not Found
```bash
# Check tool location
find . -name "tool_name.py"

# Verify tool path in scripts
which python
```

### Debug Mode

```bash
# Enable verbose output
python tools/validate_imports.py --verbose

# Check tool help
python tools/validate_imports.py --help

# Run with debug logging
DEBUG=1 python tools/validate_imports.py
```

## 📚 Documentation

### Tool-Specific Documentation
- **Import Validation**: See `validate_imports.py --help`
- **Test Runner**: See `run-tests.sh --help`
- **Development Script**: See `run.sh --help`

### Integration
- **CI/CD**: Tools integrate with GitHub Actions
- **Pre-commit**: Hooks for automated validation
- **IDE Integration**: VS Code and Cursor support
- **Documentation**: Auto-generated tool documentation

## 🤝 Contributing

### Adding New Tools
1. **Identify Need**: Determine what tool would improve development workflow
2. **Design Interface**: Plan command-line arguments and options
3. **Implement Logic**: Write robust, well-tested tool code
4. **Add Documentation**: Include comprehensive help and examples
5. **Update This README**: Document the new tool here

### Tool Standards
- **Error Handling**: Graceful error handling with helpful messages
- **Logging**: Appropriate logging levels and output
- **Testing**: Unit tests for tool functionality
- **Documentation**: Clear usage instructions and examples
- **Performance**: Efficient execution for large codebases

## 📄 License

These development tools are part of the DeepWiki project and follow the same MIT license terms.

## 🔗 Related Resources

- [Backend Documentation](../backend/README.md)
- [Frontend Documentation](../src/README.md)
- [Main Project README](../README.md)
- [Development Guidelines](../docs/development.md)
