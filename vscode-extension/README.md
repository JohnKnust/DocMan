# DocMan - Documentation Validator

**Status**: ✅ Production Ready
**Version**: 1.2.6
**Last Updated**: 2025-07-06

**Configurable documentation validation** that adapts to YOUR project's needs. Define your metadata requirements, status values, and validation rules in `.docmanrc` - DocMan validates accordingly with **real-time error detection** and **auto-fixes**.

## ⚙️ **Configuration-Driven Validation**

DocMan reads your **`.docmanrc`** configuration and validates dynamically:

```toml
# Define YOUR metadata requirements
required_metadata = ["Status", "Version", "Last Updated", "Owner"]

# Define YOUR valid status values  
valid_statuses = [
    "🟢 Live",
    "🟡 Beta", 
    "🔴 Deprecated",
    "🔵 Draft"
]

# Define YOUR validation rules
version_pattern = "semantic"  # or "custom"
date_format = "YYYY-MM-DD"   # or your format
```

**Result:** Extension shows YOUR configured values in error messages and quick fixes!

## ⚡ What it does

- **🔍 Real-time validation** - Based on YOUR .docmanrc configuration
- **🎯 Dynamic error messages** - Shows YOUR valid status values, not hardcoded ones
- **⚡ Smart quick fixes** - Suggests YOUR configured metadata fields
- **📊 Workspace overview** - Validates entire project with YOUR rules
- **🔧 Auto-discovery** - Finds .docmanrc in workspace, parent, or grandparent directories
- **🎛️ Per-project activation** - Only activates when you want it, no unnecessary irritation

## 🚀 Quick Start

### **1. Install Extension**
**Preferred method:** VS Code UI import
- Open VS Code Extensions panel
- Click `...` → `Install from VSIX`
- Select `docman-vscode-1.2.6.vsix`

**Alternative:** Command line
```bash
code --install-extension docman-vscode-1.2.6.vsix
```

### **2. Install/Configure CLI**
```bash
# Option A: Auto-install (recommended)
# Use Command Palette: "DocMan: Install CLI Tool"

# Option B: Manual install as submodule
git submodule add https://github.com/your-repo/DocMan.git
```

### **3. Automatic Setup & Activation**
**With existing config:** When you open a project with `.docmanrc`, DocMan will ask:
```
DocMan configuration detected. Enable validation for this workspace?
[Enable] [Not now] [Never for this workspace]
```

**Without config:** When no config is found, DocMan offers to create one:
```
DocMan extension is installed but no configuration found.
Would you like to create a .docmanrc configuration?
[Create Config] [Not now] [Never for this workspace]
```

**Manual control:** Use Command Palette: **"DocMan: Toggle Activation for Workspace"**

### **4. Configuration Options**
**Automatic:** Choose "Create Config" when prompted (recommended)

**Manual:** Use Command Palette: "DocMan: Open Configuration File"

```toml
# .docmanrc - Place in project root or parent directory
required_metadata = ["Status", "Version", "Last Updated"]
valid_statuses = [
    "✅ Production Ready",
    "🚧 Draft", 
    "🚫 Deprecated"
]
```

### **5. Start Validating**
- Open any `.md` file
- See real-time validation in Problems Panel
- Use quick fixes (💡) for instant corrections
- Use quick fixes for instant corrections

## 🔧 Configuration

### **Extension Settings (VS Code)**
```json
{
  "docman.autoValidateOnSave": true,
  "docman.pythonPath": "python", 
  "docman.cliPath": "./DocMan/docman/cli.py"
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

- **Add missing metadata** - Inserts YOUR configured required fields
- **Update Last Updated date** - Sets to today's date
- **Fix status values** - Shows YOUR valid status options
- **Create missing README** - Generates template with YOUR metadata
- **Fix broken links** - Removes or corrects invalid links

## 📋 **Standard Configuration & Test Files**

### **Default Configuration**
If no `.docmanrc` found, DocMan uses these defaults:

```toml
required_metadata = ["Status", "Version", "Last Updated"]
valid_statuses = [
    "✅ Production Ready",
    "🚧 Draft",
    "🚫 Deprecated", 
    "⚠️ Experimental",
    "🔄 In Progress"
]
version_pattern = "semantic"
date_format = "YYYY-MM-DD"
```

### **Test Files**
Extension includes test fixtures in `src/test/fixtures/`:
- `valid-readme.md` - Passes all validations
- `invalid-readme.md` - Contains intentional errors for testing
- `missing-metadata.md` - Missing required fields

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
