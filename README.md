# Lemmo Backend Core Package

A comprehensive Django core package that provides essential utilities, models, and GraphQL infrastructure for the Lemmo backend system.

## Features

- **Dynamic App Management**: Automatically discover and load Django apps from configuration
- **GraphQL Infrastructure**: Base classes for authenticated and unauthenticated mutations
- **Model Utilities**: Abstract base models with UUID, timestamps, and code fields
- **Configuration Management**: YAML-based configuration system
- **Error Handling**: Standardized error response format
- **Type Safety**: Full type hints throughout the codebase

## Installation

```bash
pip install lemmo-be-core
```

## Quick Start

### 1. Add to Django Settings

```python
INSTALLED_APPS = [
    # ... other apps
    'core',
]

# Core configuration
LEMMO_CONFIG = {
    'auto_generate_config': True,
    'config_file_path': 'config.yml',
}
```

### 2. Generate Configuration

```python
from core import AppManager

# Generate default config file
AppManager.generate_config()
```

### 3. Use GraphQL Mutations

```python
from core.gql.mutations import CoreAuthenticatedMutation

class CreateUserMutation(CoreAuthenticatedMutation):
    @classmethod
    def perform_mutation(cls, root, info, user, **data):
        # Your mutation logic here
        return lemmo_message(
            success=True,
            message="User created successfully",
            data={"user_id": "uuid"}
        )
```

## Configuration

The core package uses a YAML configuration file (`config.yml`) to manage app modules:

```yaml
apps:
  - name: "Authentication Module"
    description: "Handles user authentication and authorization."
    module: "lemmo_apps.authentication"
    url_prefix: "authentications"
  - name: "Inventory Module"
    description: "Handles inventory management."
    module: "lemmo_apps.inventory"
    url_prefix: "inventory"
```

## API Reference

### AppManager

Main class for managing application configuration and dynamic module loading.

#### Methods

- `generate_config(overwrite=False)`: Generate default configuration file
- `get_apps()`: Get list of loaded app modules
- `get_app_schema()`: Get GraphQL queries and mutations from apps
- `get_app_urls()`: Get URL patterns from apps

### Core Models

#### UUIDModel

Abstract base model with UUID primary key.

#### CodeModel

Abstract base model with UUID primary key and code field.

#### TimeDataStampedModel

Abstract base model with UUID primary key, created_at, and updated_at fields.

### GraphQL Mutations

#### CoreAuthenticatedMutation

Base class for mutations requiring authentication.

#### CoreUnauthenticatedMutation

Base class for mutations not requiring authentication.

### Utilities

#### lemmo_message()

Standardized response format for all API responses.

## Development

### Running Tests

```bash
python -m pytest core/tests/
```

### Code Quality

```bash
# Type checking
mypy core/

# Linting
flake8 core/

# Formatting
black core/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
