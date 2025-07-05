# Test Files

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-07-02

This directory contains demonstration files for the DocMan VS Code Extension.

## 🎯 Purpose

These files are designed to showcase different validation scenarios that users will encounter:

## 📁 Demo Files

### ✅ `valid-readme.md`
- **Purpose**: Shows proper DocMan metadata format
- **Expected**: Clean validation (good example)
- **Demonstrates**: Correct status, version, and date formatting

### ❌ `invalid-readme.md`
- **Purpose**: Demonstrates common validation errors
- **Expected**: Multiple validation issues
- **Demonstrates**:
  - Invalid status values
  - Incorrect version format
  - Invalid date format
  - Broken links

### ⚠️ `missing-metadata.md`
- **Purpose**: Shows files without required metadata
- **Expected**: Metadata violation warnings
- **Demonstrates**: Missing DocMan metadata fields

## 💡 Usage

1. **Install the DocMan VS Code Extension**
2. **Open this workspace in VS Code**
3. **Open any of the demo files**
4. **See validation results in:**
   - Problems Panel
   - Inline decorations
   - Hover tooltips
   - Status bar

## 🧪 Testing Commands

Try these commands on the demo files:
- `DocMan: Validate Current File` (Ctrl+Shift+D Ctrl+F)
- `DocMan: Validate Workspace` (Ctrl+Shift+D Ctrl+W)
- `DocMan: Update Index file` (Ctrl+Shift+D Ctrl+I)
