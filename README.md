# DocMan - Documentation Management System

**Status**: 🚧 In Development
**Version**: 0.2.0
**Last Updated**: 2025-01-15

A comprehensive, example-driven Documentation Management System that users can drop into any monorepo - with immediate validation and automation for high-quality documentation.

## 🎯 Project Overview

DocMan is a generic Documentation Management CLI tool with VS Code integration, designed to validate and maintain documentation standards in any repository. The system provides real-time validation, intelligent diagnostics, and powerful automation features.

## 🚀 Current Project Status

### ✅ Phase 1 - MVP (Complete)
**CLI Tool under `tools/docman/`**

- **📋 README Presence Validation**: Recursive checking of all directories for README.md files
- **📝 Metadata Format Enforcement**: Validation of Status, Version, and Last Updated fields
- **🔗 Link & Date Integrity**: Verification of Markdown links and date consistency
- **📚 Index Management**: Automatic management of DOCUMENTATION_INDEX.md
- **📊 Reporting & Exit Codes**: Comprehensive reports with emoji indicators
- **🧪 Tests & Documentation**: Complete test suite and documentation

### ✅ Phase 2 - VS Code Extension (Complete)
**VS Code Extension under `vscode-extension/`**

- **🔍 Real-time Validation**: Automatic validation on save with configurable debouncing
- **🚨 Advanced Diagnostics**: Integration with VS Code Problems Panel
- **🎨 Rich Visual Feedback**: Inline decorations with theme-aware styling
- **⚡ Smart Automation**: Code Actions for automatic problem resolution
- **⚙️ Comprehensive Configuration**: Extensive VS Code Settings and .docmanrc integration
- **📚 Complete Documentation**: Detailed documentation and troubleshooting guides

## 📁 Project Structure

```
DocMan/
├── 📄 README.md                    # This file - Project overview
├── 📄 InstructionSet.md           # Complete project instructions
├── 📄 PHASE2_SUMMARY.md           # Detailed Phase 2 summary
├── 📄 .docmanrc                   # Project configuration
├── 📄 .gitignore                  # Git ignore rules
├── 📄 DOCUMENTATION_INDEX.md      # Auto-generated index
│
├── 🛠️ tools/docman/               # Phase 1: CLI Tool
│   ├── 📄 cli.py                  # Main CLI entry point
│   ├── 📄 Makefile                # Development commands
│   ├── 📄 README.md               # CLI documentation
│   ├── 📁 src/                    # Source code modules
│   │   ├── 📄 config.py           # Configuration management
│   │   ├── 📄 indexer.py          # Index management
│   │   ├── 📄 reporter.py         # Output formatting
│   │   ├── 📄 utils.py            # Utility functions
│   │   └── 📁 validators/         # Validation modules
│   │       ├── 📄 readme_validator.py
│   │       ├── 📄 metadata_validator.py
│   │       └── 📄 link_validator.py
│   └── 📁 tests/                  # Test suite
│
├── 🎨 vscode-extension/           # Phase 2: VS Code Extension
│   ├── 📄 package.json            # Extension manifest
│   ├── 📄 README.md               # Extension documentation
│   ├── 📄 CHANGELOG.md            # Version history
│   ├── 📄 tsconfig.json           # TypeScript configuration
│   ├── 📁 src/                    # Extension source code
│   │   ├── 📄 extension.ts        # Main extension entry point
│   │   ├── 📄 docmanProvider.ts   # CLI integration
│   │   ├── 📄 diagnostics.ts     # Problems panel integration
│   │   ├── 📄 decorations.ts     # Inline visual indicators
│   │   ├── 📄 statusBar.ts       # Status bar integration
│   │   ├── 📄 configManager.ts   # Configuration management
│   │   ├── 📄 hoverProvider.ts   # Hover tooltips
│   │   ├── 📄 codeActionProvider.ts # Quick fixes
│   │   └── 📄 fileWatcher.ts     # File change detection
│   └── 📁 src/test/              # Extension tests
│
└── 📁 examples/                   # Example repository
    └── 📁 samplerepo/            # DynaFlow-style example
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with pyenv virtualenv
- **VS Code 1.74.0+** (for extension)
- **Node.js 16+** (for extension development)

### 1. CLI Tool Setup
```bash
# Set up Python environment
pyenv virtualenv 3.11.0 docman-env
pyenv local docman-env

# Navigate to CLI directory
cd tools/docman

# Install dependencies
make install

# Run DocMan
python cli.py --verbose
```

### 2. VS Code Extension Setup
```bash
# Navigate to extension directory
cd vscode-extension

# Install dependencies
npm install

# Compile extension
npm run compile

# Test extension (opens new VS Code instance)
code . && F5
```

## 🎯 Key Features

### CLI Tool Features
- **📋 Automatic README Validation** in all directories
- **📝 Metadata Format Enforcement** with configurable rules
- **🔗 Link Integrity Checking** for internal Markdown links
- **📚 Automatic Index Management** for DOCUMENTATION_INDEX.md
- **⚙️ Configurable Ignore Patterns** via .docmanrc
- **📊 Detailed Reports** with exit codes for CI/CD

### VS Code Extension Features
- **🔍 Real-time Validation** on save with debouncing
- **🚨 Problems Panel Integration** for centralized error tracking
- **🎨 Inline Decorations** with theme integration
- **💡 Hover Tooltips** with metadata guidance
- **⚡ Code Actions** for automatic corrections
- **⌨️ Keyboard Shortcuts** for common operations
- **📊 Status Bar Integration** with validation status

## 📋 Available Commands

### CLI Commands
```bash
python cli.py                    # Check current directory
python cli.py --verbose          # With detailed output
python cli.py --create-config    # Create .docmanrc
make run                         # Via Makefile
make test                        # Run tests
```

### VS Code Commands
- **DocMan: Validate Current File** (`Ctrl+Shift+D Ctrl+F`)
- **DocMan: Validate Workspace** (`Ctrl+Shift+D Ctrl+W`)
- **DocMan: Update Index file** (`Ctrl+Shift+D Ctrl+I`)
- **DocMan: Toggle Auto-validation on Save**
- **DocMan: Open Configuration File**
- **DocMan: Show Configuration Status**

## ⚙️ Configuration

### .docmanrc (Project Configuration)
```json
{
  "ignorePatterns": [".git", "node_modules", "venv", "__pycache__", "core"],
  "requiredMetadata": ["Status", "Version", "Last Updated"],
  "validStatuses": ["✅ Production Ready", "🚧 Draft", "🚫 Deprecated"],
  "autoFix": false,
  "verbose": false
}
```

### VS Code Settings
```json
{
  "docman.autoValidateOnSave": true,
  "docman.pythonPath": "python",
  "docman.cliPath": "./tools/docman/cli.py",
  "docman.showInlineDecorations": true,
  "docman.validationDelay": 500
}
```

## 🧪 Testing

### CLI Tests
```bash
cd tools/docman
make test                        # All tests
python -m pytest tests/ -v      # Pytest directly
make lint                        # Code quality
```

### Extension Tests
```bash
cd vscode-extension
npm test                         # All tests
npm run test -- --grep "Config" # Specific tests
```

## 🗺️ Roadmap

### 🔄 Phase 3 - Web-UI Dashboard (Planned)
- Express/Electron app for web interface
- Navigable file tree view
- Sidebar with metadata and link status
- Configurable via .docmanrc

### 🔄 Phase 4 - MkDocs + Docker Integration (Planned)
- MkDocs setup with Material theme
- Docker integration for deployment
- Automatic navigation and cross-references
- Corporate branding support

### 🔄 Phase 5 - Out-of-the-Box Scaffolding (Planned)
- Cookiecutter template for new projects
- npm init docman-template support
- Complete project scaffolding

### 🔄 Phase 6 - Release & Community (Planned)
- SemVer adoption and release management
- Community guidelines and contributing docs
- GitHub badges and marketplace publishing

## 🤝 Contributing

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m '✨ feat: add amazing feature'`
4. **Push branch**: `git push origin feature/amazing-feature`
5. **Create Pull Request**

### Commit Format
We use Gitmoji + Conventional Commits:
```
<gitmoji> type(scope): description

Examples:
✨ feat(cli): add configuration validation
🐛 fix(vscode): resolve decoration rendering issue
📚 docs(readme): update installation instructions
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic Claude** for AI-assisted development
- **VS Code Team** for the excellent Extension API
- **Python Community** for robust CLI tools
- **TypeScript Team** for type-safe development

## 📊 Project Metrics

### Development Status
- **Overall Progress**: 40% (2 of 6 phases complete)
- **CLI Tool**: ✅ 100% functional
- **VS Code Extension**: ✅ 100% functional
- **Lines of Code**: ~5000+ lines (Python + TypeScript)
- **Test Coverage**: Comprehensive unit and integration tests

### Technical Details
- **Languages**: Python 3.11+, TypeScript 4.9+
- **Frameworks**: VS Code Extension API, Node.js
- **Testing**: pytest (Python), Mocha (TypeScript)
- **Code Quality**: ESLint, mypy, black formatting
- **Architecture**: Modular, extensible components

## 🔧 Development

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd DocMan

# Python environment
pyenv virtualenv 3.11.0 docman-env
pyenv local docman-env

# Develop CLI
cd tools/docman
make install
make test

# Develop extension
cd ../../vscode-extension
npm install
npm run compile
code . # Then F5 for Extension Development Host
```

### Code Quality
```bash
# Python
make lint                        # ESLint + mypy
make format                      # black formatting
make type-check                  # mypy type checking

# TypeScript
npm run lint                     # ESLint
npm run compile                  # TypeScript compilation
```

## 🚨 Troubleshooting

### Common Issues

#### CLI not working
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd tools/docman
pip install -r requirements.txt

# Check configuration
python cli.py --create-config
```

#### VS Code Extension not loading
```bash
# Check Node.js version
node --version  # Should be 16+

# Reinstall dependencies
cd vscode-extension
rm -rf node_modules
npm install
npm run compile
```

#### Validation failing
1. **Check paths**: Ensure `tools/docman/cli.py` exists
2. **Python path**: Configure `docman.pythonPath` in VS Code Settings
3. **Permissions**: Ensure CLI is executable
4. **Check logs**: VS Code Output Panel → Select "DocMan"

## 📞 Support

### Documentation
- **CLI Documentation**: `tools/docman/README.md`
- **Extension Documentation**: `vscode-extension/README.md`
- **Configuration**: See `.docmanrc` examples
- **Troubleshooting**: Detailed guides in respective READMEs

### Community
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Contributing**: See Contributing Guidelines above

---

**Happy Documenting! 📚✨**

*Built with ❤️ and AI assistance*

**Last Update**: 2025-01-15 | **Next Phase**: Web-UI Dashboard
