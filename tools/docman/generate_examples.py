#!/usr/bin/env python3
"""
Example Structure Generator for DocMan

This script generates the example repository structure used for testing and demonstration.
The examples are not committed to git to keep the tool clean.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

def create_directory_structure():
    """Create the basic directory structure"""
    base_path = Path("examples/samplerepo")
    
    directories = [
        "apps/llm/phi4",
        "libs/config_utils", 
        "libs/phi4_monitoring",
        "libs/data_processing",
        "tools/documentation_maintenance",
        "core/legacy_module"
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def create_readme_files():
    """Create all README.md files with proper metadata"""
    base_path = Path("examples/samplerepo")
    
    readme_contents = {
        "README.md": {
            "status": "✅ Production Ready",
            "version": "3.0.0", 
            "date": "2025-06-10",
            "title": "Sample Repository",
            "content": """## Overview

This is a sample repository structure used to demonstrate DocMan functionality. It contains various applications, libraries, and tools with proper documentation structure.

## Structure

```
samplerepo/
├── apps/           # Applications
│   └── llm/        # LLM applications
├── libs/           # Shared libraries
├── tools/          # Development tools
└── core/           # Legacy/core modules (ignored)
```

## Getting Started

1. Clone the repository
2. Install dependencies
3. Run the applications

## Documentation

All modules follow the standard documentation format with required metadata:
- **Status**: Current status (✅ Production Ready, 🚧 Draft, 🚫 Deprecated)
- **Version**: Semantic version
- **Last Updated**: ISO date format

## Links

- [LLM Applications](apps/llm/README.md)
- [Configuration Utils](libs/config_utils/README.md)
- [Documentation Tools](tools/documentation_maintenance/README.md)"""
        },
        
        "apps/README.md": {
            "status": "✅ Production Ready",
            "version": "2.0.0",
            "date": "2025-06-12", 
            "title": "Applications",
            "content": """## Overview

This directory contains all applications in the sample repository.

## Available Applications

- [LLM Applications](llm/README.md) - Large Language Model applications and utilities"""
        },
        
        "apps/llm/README.md": {
            "status": "✅ Production Ready",
            "version": "2.5.0",
            "date": "2025-06-12",
            "title": "LLM Applications", 
            "content": """## Overview

Collection of Large Language Model applications and utilities.

## Applications

- [Phi4](phi4/README.md) - Main Phi4 model implementation

## Common Features

- Model loading and inference
- Batch processing capabilities
- Performance monitoring
- Configuration management

## Dependencies

- [Configuration Utils](../../libs/config_utils/README.md)
- [Monitoring Tools](../../libs/phi4_monitoring/README.md) (if available)"""
        },
        
        "apps/llm/phi4/README.md": {
            "status": "✅ Production Ready",
            "version": "1.2.3",
            "date": "2025-06-08",
            "title": "Phi4 LLM Application",
            "content": """## Overview

This is a sample LLM application using the Phi4 model. This directory demonstrates proper documentation structure with correct metadata formatting.

## Features

- Model inference capabilities
- Batch processing support
- API integration
- Performance monitoring

## Usage

```python
from phi4 import Phi4Model

model = Phi4Model()
result = model.predict("Your input text here")
```

## Configuration

See [config documentation](../../../libs/config_utils/README.md) for configuration options.

## Maintenance

This module is actively maintained. For documentation maintenance tools, see [documentation tools](../../../tools/documentation_maintenance/README.md)."""
        },
        
        "libs/README.md": {
            "status": "✅ Production Ready",
            "version": "2.0.0",
            "date": "2025-06-12",
            "title": "Libraries",
            "content": """## Overview

This directory contains shared libraries used across the sample repository.

## Available Libraries

- [Configuration Utils](config_utils/README.md) - Configuration management utilities
- [Phi4 Monitoring](phi4_monitoring/README.md) - Monitoring tools for Phi4 models

## Usage

Each library has its own README with specific usage instructions."""
        },
        
        "libs/config_utils/README.md": {
            "status": "🚧 Draft",
            "version": "0.8.1",
            "date": "2025-05-15",
            "title": "Configuration Utilities",
            "content": """## Overview

Shared configuration utilities for the sample repository. This library provides common configuration management functionality.

## Features

- Environment variable management
- Configuration file parsing
- Validation utilities
- Default value handling

## Usage

```python
from config_utils import ConfigManager

config = ConfigManager()
value = config.get('database.host', default='localhost')
```

## API Reference

### ConfigManager

Main configuration management class.

#### Methods

- `get(key, default=None)` - Get configuration value
- `set(key, value)` - Set configuration value
- `load_from_file(path)` - Load configuration from file"""
        },
        
        "libs/phi4_monitoring/README.md": {
            "status": "✅ Production Ready",
            "version": "1.0.0",
            "date": "2025-06-05",
            "title": "Phi4 Monitoring Library",
            "content": """## Overview

This library provides monitoring capabilities for Phi4 model performance and usage tracking.

## Features

- Real-time performance monitoring
- Usage analytics
- Error tracking and reporting
- Integration with monitoring dashboards

## Usage

```python
from phi4_monitoring import Monitor

monitor = Monitor()
monitor.track_inference(model, input_data)
```"""
        },
        
        "libs/data_processing/README.md": {
            "status": "🚧 Draft",
            "version": "0.1.0", 
            "date": "2025-06-12",
            "title": "Data Processing Library",
            "content": """## Overview

Data processing utilities and tools.

## Features

- Data transformation
- Batch processing
- Pipeline management

## Usage

```python
from data_processing import Pipeline

pipeline = Pipeline()
result = pipeline.process(data)
```"""
        },
        
        "tools/README.md": {
            "status": "✅ Production Ready",
            "version": "1.0.0",
            "date": "2025-06-12",
            "title": "Tools",
            "content": """## Overview

Development and maintenance tools for the sample repository.

## Available Tools

- [Documentation Maintenance](documentation_maintenance/README.md) - Tools for maintaining documentation standards"""
        },
        
        "tools/documentation_maintenance/README.md": {
            "status": "✅ Production Ready",
            "version": "2.1.0",
            "date": "2025-06-10",
            "title": "Documentation Maintenance Tools",
            "content": """## Overview

Tools and utilities for maintaining documentation across the repository. This includes automated checks, formatting, and validation.

## Tools Included

- Documentation linter
- Link checker
- Metadata validator
- Index generator

## Usage

```bash
# Run documentation checks
./check_docs.sh

# Generate documentation index
./generate_index.py

# Validate all markdown files
./validate_markdown.py
```

## Configuration

Create a `.docrc` file in the repository root:

```yaml
ignore_patterns:
  - "*.tmp"
  - "node_modules/"
  - ".git/"

required_metadata:
  - Status
  - Version
  - Last Updated
```

## Integration

These tools integrate with CI/CD pipelines and can be run automatically on commits."""
        },
        
        "core/legacy_module/README.md": {
            "status": "🚫 Deprecated",
            "version": "0.1.0",
            "date": "2024-12-01",
            "title": "Legacy Module",
            "content": """## Overview

This is a legacy module that should be ignored by documentation tools. It's located in the `core/` directory which is typically excluded from documentation validation.

## Deprecation Notice

This module is deprecated and will be removed in a future version. Please migrate to the new implementation.

## Migration Guide

See the main documentation for migration instructions."""
        }
    }
    
    for file_path, config in readme_contents.items():
        full_path = base_path / file_path
        
        content = f"""# {config['title']}

**Status**: {config['status']}  
**Version**: {config['version']}  
**Last Updated**: {config['date']}

{config['content']}
"""
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created README: {full_path}")

def create_additional_files():
    """Create additional files for testing"""
    base_path = Path("examples/samplerepo")
    
    # Create a Python file in data_processing to test missing README detection
    processor_file = base_path / "libs/data_processing/processor.py"
    with open(processor_file, 'w', encoding='utf-8') as f:
        f.write("# This directory intentionally has no README.md to test validation\n")
    print(f"✅ Created test file: {processor_file}")
    
    # Create DOCUMENTATION_INDEX.md
    index_content = """# Documentation Index

This file contains links to all documentation in the repository.


## Project Root
- [README.md](README.md) – ✅ Production Ready – 2025-06-10
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) – 🚧 Draft – 2025-01-01


## Tools
- [tools/documentation_maintenance/README.md](tools/documentation_maintenance/README.md) – ✅ Production Ready – 2025-06-10
- [tools/README.md](tools/README.md) – ✅ Production Ready – 2025-06-12


## Libraries
- [libs/config_utils/README.md](libs/config_utils/README.md) – 🚧 Draft – 2025-05-15
- [libs/phi4_monitoring/README.md](libs/phi4_monitoring/README.md) – ✅ Production Ready – 2025-06-05
- [libs/README.md](libs/README.md) – ✅ Production Ready – 2025-06-12
- [libs/data_processing/README.md](libs/data_processing/README.md) – 🚧 Draft – 2025-06-12



## Applications
- [apps/llm/README.md](apps/llm/README.md) – ✅ Production Ready – 2025-04-01
- [apps/llm/phi4/README.md](apps/llm/phi4/README.md) – ✅ Production Ready – 2025-06-08
- [apps/README.md](apps/README.md) – ✅ Production Ready – 2025-06-12

"""
    
    index_file = base_path / "DOCUMENTATION_INDEX.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"✅ Created index file: {index_file}")

def main():
    """Main function to generate example structure"""
    print("🎨 Generating DocMan example structure...")
    print("=" * 50)
    
    try:
        create_directory_structure()
        print()
        create_readme_files()
        print()
        create_additional_files()
        print()
        print("=" * 50)
        print("✅ Example structure generated successfully!")
        print()
        print("📁 Generated structure:")
        print("examples/samplerepo/")
        print("├── README.md")
        print("├── DOCUMENTATION_INDEX.md")
        print("├── apps/")
        print("│   ├── README.md")
        print("│   └── llm/")
        print("│       ├── README.md")
        print("│       └── phi4/")
        print("│           └── README.md")
        print("├── libs/")
        print("│   ├── README.md")
        print("│   ├── config_utils/")
        print("│   │   └── README.md")
        print("│   ├── phi4_monitoring/")
        print("│   │   └── README.md")
        print("│   └── data_processing/")
        print("│       ├── README.md")
        print("│       └── processor.py")
        print("├── tools/")
        print("│   ├── README.md")
        print("│   └── documentation_maintenance/")
        print("│       └── README.md")
        print("└── core/")
        print("    └── legacy_module/")
        print("        └── README.md")
        print()
        print("🚀 You can now test DocMan with: python cli.py examples/samplerepo")
        
    except Exception as e:
        print(f"❌ Error generating examples: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
