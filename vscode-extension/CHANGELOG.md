# DocMan VS Code Extension - Changelog

**Status**: ✅ Production Ready
**Version**: 1.2.6
**Last Updated**: 2025-07-05

## [1.2.6] - 2025-07-05

### 🚀 Enhanced Activation Logic - No More Dead Ends!
- **Smart config creation**: When extension is installed but no config detected, now prompts to create `.docmanrc` automatically
- **Seamless workflow**: Install → Prompted to create config → Automatically enabled and ready to use
- **No dead ends**: Extension always offers a path forward instead of staying silently disabled
- **Improved user experience**: Clear workflow with automatic enablement after config creation

### 🔧 Technical Improvements
- **Fixed activation logic**: Replaced passive "stay disabled" behavior with proactive config creation offer
- **Enhanced prompts**: Better messaging that guides users through setup process
- **Automatic enablement**: Once config is created, DocMan is immediately ready to use

### 📋 Installation Method Updates
- **Preferred method**: VS Code UI import via Extensions panel → ... → Install from VSIX
- **Updated documentation**: Clearer installation instructions with method preferences

## [1.2.5] - 2025-07-05

### 🚀 New Features - Workspace-based Activation
- **Per-project activation**: DocMan now requires explicit activation per workspace to avoid unnecessary user irritation
- **Smart detection**: Automatically prompts for activation when `.docmanrc` configuration is detected
- **Status bar toggle**: Click status bar to enable/disable DocMan for current workspace
- **Persistent settings**: Workspace activation preference is remembered across VS Code sessions

### ✨ Enhanced Quick Fixes
- **Dynamic README creation**: README templates now use configuration-based metadata fields
- **Configuration-aware metadata**: Quick fixes respect your `.docmanrc` settings for required fields and valid statuses
- **Improved user experience**: More intuitive activation flow with clear user choices

### 🔧 Technical Improvements
- **Removed static template dependency**: No longer relies on `.docmanrc.template` file
- **Better error handling**: Improved configuration parsing and fallback mechanisms
- **Enhanced TypeScript support**: Complete type definitions for configuration management

### 📋 Commands Added
- **DocMan: Toggle Activation for Workspace** - Enable/disable DocMan for current project

## [1.2.4] - 2025-07-04

### 🐛 Fixed - Critical Config Parsing Implementation
- **Missing Config Parser**: Added complete `getDocManConfig()` and `parseDocManConfig()` methods to ConfigManager
  - Extension was missing the actual config parsing implementation, always falling back to hardcoded defaults
  - Now properly reads and parses `.docmanrc` files with multiline array support
  - Correctly handles `valid_statuses`, `required_metadata`, `version_pattern`, and `date_format` from config files

### ✨ Enhanced
- **Dynamic Error Messages**: Error messages now use actual config values instead of hardcoded defaults
- **True Configuration-Driven Validation**: Extension now adapts to custom `.docmanrc` settings in real-time
- **Improved Config File Discovery**: Better search logic for config files in parent directories

### 🔧 Technical Details
- Implemented robust multiline array parsing for `.docmanrc` format
- Added proper handling of single-line and multi-line configuration arrays
- Enhanced config file search with fallback to template files

## [1.2.3] - 2025-07-02

### 🐛 Fixed
- **Critical: "Validate Current File" now works correctly**: Fixed issue where single file validation showed "valid" for files with problems
- **Single file validation**: Extension now validates parent directory and filters results for the specific file
- **Accurate error reporting**: Files with metadata violations now correctly show errors in Problems Panel

## [1.2.2] - 2025-07-02

### 📝 Documentation
- **Complete README overhaul**: Now emphasizes configuration-driven validation
- **Configuration-first approach**: Shows how .docmanrc drives dynamic validation
- **Enhanced Quick Start**: Includes CLI installation and configuration setup
- **Clear structure**: Separated standard config from customization options

## [1.2.1] - 2025-07-02

### 🔧 Changed
- **CLI integration**: Updated to work with DocMan CLI 1.0.1 (validates ALL markdown files)
- **Validation scope**: Extension now validates all .md files, not just README files
- **Test structure**: Cleaned up test organization with proper fixtures directory

### 🐛 Fixed
- **Test file organization**: Moved test files to src/test/fixtures/ for better structure
- **Removed clutter**: Cleaned up old .vsix files and loose test files

### 🧹 Maintenance
- **Project cleanup**: Removed development artifacts and organized test structure
- **Documentation**: Updated to reflect all markdown files require metadata

## [1.2.0] - 2025-07-02

### ✨ Added
- **Auto-CLI installation**: Extension can install DocMan CLI automatically via submodule or download
- **Enhanced config discovery**: Better support for parent directory configs (submodule setup)
- **New commands**: "Install CLI Tool", "Find CLI Tool" for easier setup
- **Improved config status**: Shows detailed config location and search paths

### 🔧 Changed
- **Config search order**: Prioritizes parent directory for submodule usage
- **Better error messages**: Clear guidance when CLI not found
- **Documentation**: Separated extension vs CLI configuration details

### 🐛 Fixed
- **Submodule config support**: Extension now properly finds parent directory .docmanrc files
- **CLI path resolution**: Auto-discovery of CLI in common locations

## [1.1.0] - 2025-07-02

### ✨ Added
- **Dynamic configuration-aware error messages**: Extension now reads `.docmanrc` and shows user-configured valid status values
- **Hybrid CLI + Config approach**: Combines CLI output with configuration-specific suggestions
- **Smart error enhancement**: Automatically detects error types and provides relevant configuration-based help

### 🔧 Changed
- **Error messages now dynamic**: Instead of hardcoded "use ✅ Production Ready, 🚧 Draft", shows actual configured values
- **Configuration parsing**: Extension parses `.docmanrc` for `valid_statuses`, `required_metadata`, `version_pattern`, `date_format`
- **Fallback mechanism**: Uses CLI output when configuration is unavailable

## [1.0.3] - 2025-07-02

### 🐛 Fixed
- **Incorrect error categorization**: `invalid-readme.md` now shows specific metadata violations instead of "Missing README"
- **Better error messages**: More descriptive messages for invalid status, version, and date formats
- **Logical error assignment**: Files with content no longer marked as "missing README"

## [1.0.2] - 2025-07-02

### 🐛 Fixed
- **Workspace validation**: Fixed incorrect error assignment to files
- **Duplicate diagnostics**: Removed duplicate error entries in Problems Panel
- **File-specific validation**: Only show relevant errors per file
- **CLI output parsing**: Improved parsing of DocMan CLI validation results

## [1.0.1] - 2025-07-02

### 🐛 Fixed
- **Markdown-only validation**: Current file validation now restricted to .md files
- **Diagnostics cross-contamination**: Fixed errors appearing in wrong files
- **Workspace validation**: Improved error detection and reporting

### 📝 Changed
- **Extension description**: More concise, developer-focused marketplace description
- **README**: Streamlined documentation with actionable insights

## [1.0.0] - 2025-07-02

### 🎉 Initial Release

#### ✨ Core Features
- **Real-time validation** on file save with debouncing
- **Problems Panel integration** with detailed diagnostics
- **Inline decorations** with theme-aware styling
- **Quick fixes** for common documentation issues
- **Status bar integration** with validation status
- **Hover tooltips** for metadata and links

#### 📋 Commands
- Validate Current File (`Ctrl+Shift+D F`)
- Validate Workspace (`Ctrl+Shift+D W`)
- Update Index (`Ctrl+Shift+D I`)
- Toggle Auto-validation
- Open/Show Configuration

#### ⚙️ Configuration
- Auto-validation on save
- Python and CLI path settings
- Decoration and tooltip toggles
- Validation delay configuration

#### 🔧 Technical
- TypeScript with strict mode
- Modular architecture
- CLI integration with error handling
- Comprehensive test suite
- VS Code 1.74+ compatibility
