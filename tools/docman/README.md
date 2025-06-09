# DocMan - Documentation Management CLI Tool

**Status**: ✅ Production Ready  
**Version**: 0.1.0  
**Last Updated**: 2025-06-12

A generic, example-driven Documentation Management CLI tool that can be dropped into any monorepo to validate and maintain documentation standards.

## Features

- 📋 **README Presence Validation** - Ensures all directories have README.md files
- 🔍 **Metadata Format Enforcement** - Validates Status, Version, and Last Updated fields
- 🔗 **Link Integrity Checking** - Verifies all markdown links point to existing files
- 📅 **Date Consistency Reporting** - Identifies when parent READMEs are older than children
- 📚 **Index Management** - Automatically maintains DOCUMENTATION_INDEX.md
- 🎯 **Smart Ignore Patterns** - Respects common ignore patterns (.git, node_modules, core/, etc.)
- 📊 **Comprehensive Reporting** - Beautiful terminal output with emojis and proper exit codes

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd DocMan/tools/docman

# Setup Python 3.11 environment
pyenv virtualenv 3.11.0 docman-env
pyenv local docman-env

# Install dependencies
make install
```

### Basic Usage

```bash
# Check current directory
python cli.py

# Check specific repository
python cli.py /path/to/your/repo

# Verbose output
python cli.py --verbose /path/to/your/repo

# Using Makefile
make run                    # Check current directory
make run-verbose           # Verbose output
make run-report            # Detailed report
```

## Example Output

```
============================================================
📊 DOCUMENTATION VALIDATION SUMMARY
============================================================

🚧 Missing READMEs (2)
  • Missing README: tools
  • Missing README: libs/data_processing

🚧 Metadata violations (1)
  • Bad metadata in libs/utils/README.md: invalid version format "not-a-version"

🚧 Broken links (1)
  • Broken link in README.md: nonexistent/file.md

🚧 Date inconsistencies (1)
  • Parent apps/README.md (2025-04-01) is older than child apps/web/README.md (2025-06-08)

✅ New index entries (3)
  • Added tools/README.md to index
  • Added libs/README.md to index
  • Added apps/README.md to index
------------------------------------------------------------
🚧 Found 4 documentation issues
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install dependencies (pytest, black, flake8, mypy) |
| `make check-syntax` | Check Python syntax |
| `make run` | Run DocMan on current directory |
| `make run-fix` | Run DocMan with auto-fix enabled |
| `make run-verbose` | Run DocMan with verbose output |
| `make run-report` | Run DocMan with detailed report |
| `make validate` | Run all validation checks |
| `make test` | Run unit tests |
| `make lint` | Run linting checks |
| `make format` | Format code with black |
| `make type-check` | Run type checking with mypy |
| `make clean` | Clean up temporary files |
| `make quick-check` | Run quick syntax and basic tests |

## Metadata Format

DocMan expects README.md files to have metadata in this format:

```markdown
# Your Title

**Status**: ✅ Production Ready  
**Version**: 1.2.3  
**Last Updated**: 2025-06-08

Your content here...
```

### Valid Status Values

- ✅ Production Ready
- 🚧 Draft
- 🚫 Deprecated
- ⚠️ Experimental
- 🔄 In Progress

### Version Format

Semantic versioning (x.y.z) is required, e.g., `1.2.3`, `0.1.0`

### Date Format

ISO date format (YYYY-MM-DD) is required, e.g., `2025-06-08`

## Testing

```bash
# Run all tests
make test

# Run specific test modules
python -m pytest tests/test_validators.py -v
python -m pytest tests/test_indexer.py -v
python -m pytest tests/test_reporter.py -v
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# All validation checks
make validate
```

### Project Structure

```
tools/docman/
├── cli.py                 # Main CLI entry point
├── src/                   # Source code
│   ├── validators/        # Validation modules
│   │   ├── readme_validator.py
│   │   ├── metadata_validator.py
│   │   └── link_validator.py
│   ├── indexer.py         # Index management
│   ├── reporter.py        # Output formatting
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
├── Makefile              # Development commands
└── README.md             # This file
```

## Exit Codes

- **0**: All documentation checks passed
- **1**: Issues found (missing READMEs, metadata violations, broken links)

Note: Date inconsistencies are reported as warnings and don't affect the exit code.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run validation: `make validate`
6. Submit a pull request

## License

[Add your license here]
