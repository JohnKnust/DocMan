# DocMan - Documentation Validator

Instant documentation validation with **real-time error detection**, **auto-fixes**, and **Problems Panel integration**. Enforces metadata standards for ALL markdown files and catches broken links as you type.

## ⚡ What it does

- **🔍 Real-time validation** - See issues instantly in Problems Panel
- **🎯 Inline decorations** - Errors highlighted directly in your markdown
- **⚡ Quick fixes** - One-click solutions for common issues
- **📋 Metadata enforcement** - Ensures Status, Version, Last Updated fields
- **🔗 Link validation** - Catches broken internal/external links
- **📊 Workspace overview** - Validate entire documentation at once

## 🚀 Quick Start

1. **Install extension**
2. **Open any `.md` file**
3. **See validation results** in Problems Panel
4. **Use quick fixes** (💡 icon) to resolve issues instantly

## ⌨️ Commands

| Command | Shortcut | Action |
|---------|----------|--------|
| Validate Current File | `Ctrl+Shift+D F` | Check active markdown file |
| Validate Workspace | `Ctrl+Shift+D W` | Check all documentation |
| Update Index | `Ctrl+Shift+D I` | Refresh documentation index |

## 📋 Required Metadata Format

DocMan enforces this metadata structure in README files:

```markdown
# Your Project Title

**Status**: ✅ Production Ready
**Version**: 1.2.3
**Last Updated**: 2025-07-02

Your content here...
```

**Valid Status Values:**
- ✅ Production Ready
- 🚧 Draft
- 🚫 Deprecated
- ⚠️ Experimental
- 🔄 In Progress

## 🔧 Configuration

### **Extension Settings (VS Code)**
```json
{
  "docman.autoValidateOnSave": true,
  "docman.pythonPath": "python",
  "docman.cliPath": "./docman/cli.py",
  "docman.showInlineDecorations": true,
  "docman.validationDelay": 500
}
```

### **DocMan Configuration (.docmanrc)**
**Auto-discovery order:**
1. **Workspace root**: `.docmanrc`
2. **Parent directory**: `../.docmanrc` ⭐ **Recommended for submodules**
3. **Two levels up**: `../../.docmanrc` (nested submodules)
4. **Template fallback**: `.docmanrc.template`

**Submodule Setup (Recommended):**
```
your-project/
├── .docmanrc                    ← Main config
├── DocMan/                      ← Git submodule
│   └── vscode-extension/        ← Extension
└── other-submodules/
```

**Check active config:** Use `DocMan: Show Configuration Status`

## 💡 Quick Fixes Available

- **Add missing metadata** - Inserts required Status/Version/Date fields
- **Update Last Updated date** - Sets to today's date
- **Create missing README** - Generates template with metadata
- **Fix broken links** - Removes or corrects invalid links

## 🚨 Troubleshooting

### **CLI Not Found**
1. **Use auto-discovery:** `DocMan: Find CLI Tool`
2. **Install automatically:** `DocMan: Install CLI Tool`
3. **Manual setup:** Update `docman.cliPath` setting

### **Configuration Issues**
1. **Check active config:** `DocMan: Show Configuration Status`
2. **Missing config:** Extension will show search locations
3. **Submodule setup:** Place `.docmanrc` in parent directory

### **Validation Not Working**
- **File type:** Only works on `.md` files
- **Check logs:** Output Panel → "DocMan"
- **Python path:** Verify `docman.pythonPath` setting

### **Auto-Installation Options**
- **Git Submodule:** Recommended for teams
- **Direct Download:** For standalone projects
- **Manual Setup:** Full control over installation

---

**Requirements:** VS Code 1.74+, Python 3.11+ (auto-installed if needed)
