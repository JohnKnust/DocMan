# DocMan - Documentation Management CLI Tool

**Status**: ✅ Production Ready
**Version**: 1.0.3
**Last Updated**: 2025-07-06

A generic, example-driven Documentation Management CLI tool that can be dropped into any monorepo to validate and maintain documentation standards. **V1.0.3 - Production Ready with new 2-part index structure, enhanced management and smart configuration.**

## Features

- 📋 **README Presence Validation** - Ensures all directories have README.md files
- 🔍 **Metadata Format Enforcement** - Validates Status, Version, and Last Updated fields
- 🔗 **Link Integrity Checking** - Verifies all markdown links point to existing files
- 📅 **Date Consistency Reporting** - Identifies when parent READMEs are older than children
- 📚 **Smart Index Management** - Automatically maintains DOCUMENTATION_INDEX.md with new 2-part structure (README hierarchy + Others section)
- 🎯 **Smart Ignore Patterns** - Respects common ignore patterns (.git, node_modules, core/, etc.)
- 📊 **Comprehensive Reporting** - Beautiful terminal output with emojis and proper exit codes

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd DocMan/docman

# Setup Python 3.11 environment
pyenv virtualenv 3.11.0 docman-env
pyenv local docman-env

# Install dependencies
make install

# Generate example structure for testing
python generate_examples.py
```

### Example Structure Generation

DocMan includes a script to generate example repository structures for testing and demonstration:

```bash
# Generate example structure
python generate_examples.py

# This creates examples/samplerepo/ with:
# - Proper README.md files with metadata
# - Directory structure mimicking real projects
# - Test cases for validation (missing READMEs, broken links, etc.)
```

**Note**: The examples/ directory is not committed to git to keep the tool clean. Run the generation script whenever you need fresh examples.

### Typical Workflow

```bash
# 1. First time setup
make install                    # Install dependencies
make generate-examples         # Create example structure

# 2. Test DocMan on examples
make run-examples              # Generate + run DocMan on examples
# OR step by step:
python generate_examples.py    # Generate examples
python cli.py examples/samplerepo --verbose  # Run DocMan

# 3. Use on your own repository
python cli.py /path/to/your/repo --verbose

# 4. Development workflow
make test                      # Run unit tests
make lint                      # Check code quality
make format                    # Format code
```

### Basic Usage

```bash
# Check current directory
python cli.py

# Check the generated example
python cli.py examples/samplerepo

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
docman/
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

## ⚙️ Configuration

DocMan uses a flexible configuration loading strategy designed for submodule usage.

### Configuration File Location

DocMan searches for `.docmanrc` in the following order:
1. **DOCMAN_CONFIG environment variable** (if set)
2. **Parent directory of docman/ folder** (recommended for submodules)
3. Current working directory
4. Parent directories up to git root
5. Default configuration (fallback)

### Recommended Structure for Submodules

```
your-project/
├── .docmanrc          # Configuration file (recommended location)
├── docman/            # DocMan submodule
│   ├── .docmanrc.template  # Template file
│   └── ...
└── your-files...
```

### Quick Setup

```bash
# Create configuration template
python cli.py --create-config

# Copy template to project root (if using as submodule)
cp .docmanrc.template ../.docmanrc

# Edit configuration as needed
nano ../.docmanrc  # or nano .docmanrc if in same directory
```

### Configuration Format

```ini
# DocMan Configuration File
root_directory = "."
index_file = "DOCUMENTATION_INDEX.md"
recreate_index = true
strict_validation = true

required_metadata = [
    "Status",
    "Version",
    "Last Updated"
]

ignore_patterns = [
    ".git/",
    "node_modules/",
    "venv/",
    "__pycache__/",
    "*.tmp",
    "*.log"
]

verbose_output = false
colored_output = true
emoji_indicators = true
generate_reports = true
exit_on_errors = true
```

### Environment Variable Override

You can override the configuration file location:

```bash
export DOCMAN_CONFIG="/path/to/custom/.docmanrc"
python cli.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run validation: `make validate`
6. Submit a pull request

## License

[Add your license here]
