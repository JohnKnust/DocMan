# Changelog

All notable changes to DocMan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-07-04

### 🐛 Fixed - Critical Config Parsing Bug
- **Python CLI Config Parser**: Fixed critical bug where `valid_statuses`, `version_pattern`, and `date_format` were ignored from `.docmanrc` files
  - The parser was reading config files correctly but not applying values due to missing keys in `key_mapping` dictionary
  - Now properly supports dynamic configuration for all metadata validation rules
  - Both Python CLI and VS Code extension now correctly read and apply custom status values from `.docmanrc`

### ✨ Added
- Public `config_path` and `is_fallback` properties to `DocManConfig` class for better config introspection
- Enhanced config debugging capabilities

### 🔧 Technical Details
- Added missing `'valid_statuses'`, `'version_pattern'`, and `'date_format'` keys to `_set_config_value()` method
- Enhanced `DocManConfig` dataclass with proper property accessors for private attributes

## [1.0.1] - 2025-07-02

### 🔧 Changed
- **Metadata validation scope**: Now validates ALL markdown files, not just README files
- **Comprehensive coverage**: Every .md file in repository must have proper metadata (Status, Version, Last Updated)

### 🐛 Fixed
- **Validation gap**: Previously only files with "readme" in name were validated
- **Consistency**: All markdown files now follow same metadata requirements

## [1.0.0] - 2025-07-02

### 🎉 Initial Production Release

DocMan V1.0.0 is now production ready! This release provides a complete, robust documentation management system that can be dropped into any monorepo.

**Includes VS Code Extension v1.2.1** - Real-time validation with inline errors and auto-fixes.

### ✅ Added

#### Core Features
- **📋 README Presence Validation**: Recursive checking of all directories for README.md files
- **📝 Metadata Format Enforcement**: Validation of Status, Version, and Last Updated fields
- **🔗 Link & Date Integrity**: Verification of Markdown links and date consistency
- **📚 Index Management**: Automatic management of DOCUMENTATION_INDEX.md
- **📊 Reporting & Exit Codes**: Comprehensive reports with emoji indicators

#### Configuration System
- **⚙️ Smart Configuration Loading**: Flexible .docmanrc loading with multiple search paths
- **🔄 Submodule-Ready Design**: Clean separation of configuration and code
- **💡 Fallback Mechanism**: Automatic fallback to template configuration
- **🚨 User-Friendly Feedback**: Clear warnings when fallback is active
- **🌍 Environment Variable Support**: DOCMAN_CONFIG override capability

#### Configuration Search Order
1. `DOCMAN_CONFIG` environment variable path (if set)
2. Parent of parent directory (e.g., `/project/.docmanrc` when DocMan is at `/project/DocMan/docman/`)
3. Parent directory of docman/ folder (e.g., `/project/DocMan/.docmanrc`)
4. Current working directory
5. Parent directories up to git root
6. Template file as fallback (`.docmanrc.template`)

#### CLI Features
- **🎯 Intuitive Commands**: Simple CLI with helpful options
- **📝 Template Generation**: `--create-config` for easy setup
- **🔍 Verbose Mode**: Detailed output with configuration status
- **⚙️ Configuration Override**: `--config` parameter for custom config paths

#### Developer Experience
- **🧪 Comprehensive Test Suite**: Full test coverage for all components
- **📚 Complete Documentation**: Detailed README files and usage examples
- **🛠️ Development Tools**: Makefile with common development tasks
- **🎨 Code Quality**: Linting, formatting, and type checking
- **🔌 VS Code Extension**: Real-time validation with Problems Panel integration (v1.2.1)

#### Submodule Integration
- **📁 Clean Structure**: Template in DocMan directory, config in parent
- **🔄 No Submodule Changes**: All configuration external to submodule
- **💡 Clear Guidance**: Helpful messages for configuration setup
- **🎯 Production Ready**: Designed for real-world submodule usage

### 🏗️ Technical Implementation

#### Architecture
- **Modular Design**: Clean separation of validators, indexer, reporter, and utilities
- **Flexible Configuration**: Custom parser supporting multiple formats
- **Robust Error Handling**: Graceful fallbacks and clear error messages
- **Performance Optimized**: Efficient file scanning with ignore patterns

#### File Structure
```
DocMan/
├── .docmanrc.template          # Configuration template
├── README.md                   # Project documentation
├── CHANGELOG.md               # This file
├── InstructionSet.md          # Development instructions
└── docman/                    # CLI tool
    ├── cli.py                 # Main entry point
    ├── README.md              # CLI documentation
    ├── Makefile               # Development commands
    ├── src/                   # Source code
    │   ├── config.py          # Configuration management
    │   ├── indexer.py         # Index management
    │   ├── reporter.py        # Output formatting
    │   ├── utils.py           # Utility functions
    │   └── validators/        # Validation modules
    └── tests/                 # Test suite
```

### 🎯 Production Ready

This V1.0.0 release is stable and ready for production use in:
- Monorepo documentation validation
- CI/CD pipeline integration
- Team documentation standards
- Submodule integration scenarios

---

## [Unreleased]

### Planned Features
- Web UI Dashboard (Phase 3)
- MkDocs Integration (Phase 4)
- Advanced Reporting Features
- VS Code Extension enhancements

---

**Happy Documenting! 📚✨**
