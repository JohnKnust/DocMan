# Configuration Utilities

**Status**: 🚧 Draft  
**Version**: 0.8.1  
**Last Updated**: 2025-05-15

## Overview

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
- `load_from_file(path)` - Load configuration from file
