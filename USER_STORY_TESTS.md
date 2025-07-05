# DocMan User Story Tests

**Status**: ✅ Production Ready
**Version**: 1.2.6
**Last Updated**: 2025-07-05

This document provides comprehensive user story tests for both the DocMan CLI and VS Code Extension. These tests validate the key features and user workflows implemented in version 1.2.6.

## 📋 Overview of Changes

### 🔧 **CLI Modifications (docman/)**
1. **Enhanced --create-config Option**
   - Clearer description: "Create standardized .docmanrc.template with defaults"
   - Improved output messages
   - Removed static `.docmanrc.template` file dependency

2. **Implemented --fix Parameter**
   - New `src/autofix.py` with AutoFixer class
   - Batch creation of README files with user confirmation
   - Dynamic metadata based on `.docmanrc` configuration

3. **Configuration Cleanup**
   - Removed template fallback logic
   - Clean separation between dynamic generation and static files

### 🎨 **VS Code Extension Modifications (vscode-extension/)**
1. **Workspace-based Activation**
   - Popup on `.docmanrc` detection: "Enable validation for this workspace?"
   - Clickable Status Bar toggle
   - Persistent workspace settings

2. **Dynamic Quick Fixes**
   - README creation now uses `.docmanrc` configuration
   - Metadata quick fixes respect `required_metadata` and `valid_statuses`

3. **New Icon**
   - Added `icon.svg` and `icon.png`
   - Professional design with document + checkmark + gear

4. **Version Update**
   - Version 1.2.4 → 1.2.5
   - Updated changelog

## 🧪 CLI User Story Tests

### User Story 0: Developer wants to validate documentation quality (Core Functionality)
**As a** developer
**I want to** validate my project's documentation standards
**So that** I can maintain consistent, high-quality documentation across my repository

#### Test Steps:
```bash
cd docman

# Test core validation functionality
python cli.py --verbose
python cli.py examples/samplerepo --verbose
```

#### Expected Results:
- ✅ Scans all directories for README files
- ✅ Validates metadata format (Status, Version, Last Updated)
- ✅ Checks for broken links
- ✅ Verifies date consistency
- ✅ Updates DOCUMENTATION_INDEX.md automatically
- ✅ Provides clear error reports with emoji indicators
- ✅ Returns appropriate exit codes (0 = success, 1 = issues found)

### User Story 1: Developer wants to set up DocMan configuration
**As a** developer  
**I want to** create a standardized configuration template  
**So that** I can customize DocMan for my project needs

#### Test Steps:
```bash
cd docman

# Test configuration template creation
python cli.py --create-config
ls -la ../.docmanrc.template
```

#### Expected Results:
- ✅ Creates `.docmanrc.template` in parent directory
- ✅ Shows message: "Created standardized configuration template"
- ✅ Provides clear instructions for customization
- ✅ Template contains recommended default settings

### User Story 2: Developer wants to automatically fix missing documentation
**As a** developer  
**I want to** batch-create missing README files  
**So that** I can quickly establish documentation structure

#### Test Steps:
```bash
# Create test environment
mkdir -p test-fix/subdir1 test-fix/subdir2
echo "# Test" > test-fix/subdir1/some-file.md

# Test auto-fix functionality
python cli.py test-fix --fix --verbose
```

#### Expected Results:
- ✅ Detects missing README files
- ✅ Prompts for user confirmation
- ✅ Creates README files with dynamic metadata from `.docmanrc`
- ✅ Uses configured `required_metadata` and `valid_statuses`
- ✅ Reports number of files created

### User Story 3: Developer wants to validate documentation
**As a** developer
**I want to** run comprehensive documentation validation
**So that** I can ensure quality standards

#### Test Steps:
```bash
# Test basic validation
python cli.py --help
python cli.py --verbose

# Test validation on test files to see error output
python cli.py vscode-extension/src/test/fixtures --verbose

# Run test suite
make test
```

#### Expected Results:
- ✅ Help shows updated parameter descriptions
- ✅ Verbose output shows configuration status
- ✅ All 39 tests pass
- ✅ No template fallback warnings
- ✅ Test files demonstrate validation errors (invalid-readme.md shows multiple issues)
- ✅ Review output shows how validation errors are displayed to users

## 🎨 VS Code Extension User Story Tests

### User Story 4: Developer wants per-project DocMan activation
**As a** developer
**I want to** enable DocMan only for specific projects
**So that** I'm not unnecessarily interrupted in other projects

**Note**: Extension works when installed but no config detected - user can use commands to create config and enable functionality.

#### Test Setup:
```bash
cd vscode-extension

# Compile extension
npm run compile

# Create test workspace
mkdir -p test-workspace/subproject
cd test-workspace

# Install extension (choose one method):
# Method 1: VS Code UI import (preferred)
# Extensions panel → ... → Install from VSIX → select docman-vscode-1.2.6.vsix

# Method 2: From VS Code Extensions marketplace (when available)
# Search for "DocMan" in Extensions panel

# Method 3: Command line installation
code --install-extension ../docman-vscode-1.2.6.vsix

# Open workspace
code .

# Create .docmanrc using DocMan command (after extension is active)
# Use Command Palette: "DocMan: Create Configuration Template"
```

#### Test Steps:
1. Open VS Code in workspace with `.docmanrc`
2. Observe activation popup
3. Test status bar toggle
4. Verify workspace persistence

#### Expected Results:
- ✅ Popup appears: "DocMan configuration detected. Enable validation for this workspace?"
- ✅ Options: [Enable] [Not now] [Never for this workspace]
- ✅ Status bar shows "DocMan: Ready" when enabled
- ✅ Status bar shows "DocMan: Disabled (click to enable)" when disabled
- ✅ Clicking status bar toggles activation
- ✅ Setting persists across VS Code sessions

### User Story 5: Developer wants dynamic documentation fixes
**As a** developer
**I want to** get quick fixes based on my project's configuration
**So that** the suggestions match my documentation standards

**Note**: This tests VS Code extension quick fixes, different from existing test files which demonstrate validation errors. This tests the interactive fix functionality.

#### Test Setup:
```bash
# Create test README with missing metadata
cat > README.md << 'EOF'
# Test Project

Some content without metadata.
EOF
```

#### Test Steps:
1. Open `README.md` in VS Code
2. Observe validation errors
3. Use quick fix (💡 icon)
4. Verify dynamic metadata insertion

#### Expected Results:
- ✅ Shows error: "missing metadata fields"
- ✅ Quick fix available: "Add missing metadata fields"
- ✅ Inserts metadata based on `.docmanrc` `required_metadata`
- ✅ Uses first `valid_statuses` value as default status
- ✅ Adds current date for "Last Updated"
- ✅ Custom fields get placeholder values (e.g., "Owner": "TODO", "Version": "1.0.0")

### User Story 6: Developer wants to manage workspace activation
**As a** developer  
**I want to** easily toggle DocMan activation  
**So that** I can control when validation runs

#### Test Steps:
1. Use Command Palette: `Ctrl+Shift+P`
2. Search for "DocMan: Toggle Activation for Workspace"
3. Execute command
4. Verify status changes

#### Expected Results:
- ✅ Command available in palette
- ✅ Status bar updates immediately
- ✅ Validation starts/stops accordingly
- ✅ Clear feedback messages shown
- ✅ Diagnostics cleared when disabled

## 🔄 Isolated Testing Environments

These testing scenarios ensure that each component (CLI and VS Code Extension) works independently without interference from other tools or extensions.

### CLI Isolated Testing:
```bash
# Test CLI without Extension interference
cd docman
python cli.py . --verbose
python cli.py --create-config
python cli.py test-directory --fix
```

### Extension Isolated Testing:
```bash
# Test Extension without other extensions
code --disable-extensions --install-extension docman-vscode-1.2.6.vsix test-workspace
```

## ✅ Acceptance Criteria Summary

### CLI Acceptance Criteria:
- [ ] `--create-config` creates standardized template with clear messaging
- [ ] `--fix` prompts for confirmation and creates dynamic README files
- [ ] Configuration respects `.docmanrc` settings for metadata and statuses
- [ ] All existing tests continue to pass
- [ ] No static template file dependencies

### Extension Acceptance Criteria:
- [ ] Workspace activation popup appears on `.docmanrc` detection
- [ ] Status bar toggle works and persists settings
- [ ] Quick fixes use dynamic configuration from `.docmanrc`
- [ ] README creation respects project-specific metadata requirements
- [ ] Extension only activates when explicitly enabled per workspace

## 🚀 Getting Started

1. **For CLI testing**: Navigate to `docman/` directory and follow CLI test steps
2. **For Extension testing**: Navigate to `vscode-extension/` directory and follow Extension test steps
3. **For integrated testing**: Use both tools together in a real project environment

Each test scenario includes setup instructions, step-by-step procedures, and clear acceptance criteria to ensure consistent validation of DocMan's functionality.
