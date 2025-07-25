import os
from django.conf import settings


def get_project_root() -> str:
    """
    Returns the Django project root directory using settings.BASE_DIR.
    This function delays access to BASE_DIR until after settings are loaded.
    """
    return getattr(settings, "BASE_DIR", os.getcwd())  # fallback to cwd just in case


def get_config_file_path() -> str:
    return os.path.join(get_project_root(), "config.yml")


DEFAULT_APPS = [
    {
        "name": "Authentication Module",
        "description": "Handles user authentication and authorization.",
        "module": "lemmo_apps.authentication",
        "url_prefix": "authentications",
    },
    {
        "name": "Inventory Module",
        "description": "Handles inventory management.",
        "module": "lemmo_apps.inventory",
        "url_prefix": "inventory",
    },
    {
        "name": "Location Module",
        "description": "Handles location management & Facilities.",
        "module": "lemmo_apps.location",
        "url_prefix": "locations",
    },
    {
        "name": "Requisition Module",
        "description": "Handles requisition management.",
        "module": "lemmo_apps.requisition",
        "url_prefix": "requisitions",
    },
    {
        "name": "Stock Module",
        "description": "Handles stock management.",
        "module": "lemmo_apps.stock",
        "url_prefix": "stocks",
    },
    {
        "name": "Dashboard Module",
        "description": "Handles dashboard management.",
        "module": "lemmo_apps.dashboard",
        "url_prefix": "dashboards",
    },
    {
        "name": "FHIR API Module",
        "description": "Handles FHIR data management.",
        "module": "lemmo_apps.fhir_api",
        "url_prefix": "fhir",
    },
    {
        "name": "Integration Module",
        "description": "Handles integration with external systems.",
        "module": "lemmo_apps.integration",
        "url_prefix": "integrations",
    },
    {
        "name": "Logistics Module",
        "description": "Handles logistics and transportation management.",
        "module": "lemmo_apps.logistics",
        "url_prefix": "logistics",
    },
    {
        "name": "Supplier Module",
        "description": "Handles supplier management and relationships.",
        "module": "lemmo_apps.supplier",
        "url_prefix": "suppliers",
    },
    {
        "name": "Order Module",
        "description": "Handles order management and processing.",
        "module": "lemmo_apps.order",
        "url_prefix": "orders",
    },
]

LEMMO_DEFAULT_CONFIG_DATA = {
    "apps": DEFAULT_APPS,
}

# Version information
__version__ = "0.1.0"
__author__ = "2MCorp"
__email__ = "contact@2mcorp.com"

# Export main classes and functions
from .app_manager import AppManager
from .app_utils import (
    lemmo_message,
    success_message,
    error_message,
    warning_message,
    info_message,
    validate_required_fields,
    sanitize_data,
    LemmoResponse,
    MessageType,
)

# Models are imported lazily to avoid Django app registry issues
# Use get_abstract_models() function to access models when Django is ready
from .gql.mutations.core import (
    CoreAuthenticatedMutation,
    CoreUnauthenticatedMutation,
    MutationError,
    ValidationError,
    PermissionError,
    BusinessLogicError,
)
from .gql.queries.core import (
    CoreAuthenticatedQuery,
    CoreUnauthenticatedQuery,
    PaginatedQuery,
    FilteredQuery,
    QueryError,
    QueryValidationError,
    QueryPermissionError,
)


# Convenience functions
def get_app_info():
    """Get information about all configured apps."""
    return AppManager.get_app_info()


def get_schema_info():
    """Get information about the GraphQL schema."""
    from .schema import get_schema_info

    return get_schema_info()


def reload_schema():
    """Reload the GraphQL schema."""
    from .schema import reload_schema

    return reload_schema()


def generate_config(overwrite=False):
    """Generate the default configuration file."""
    return AppManager.generate_config(overwrite=overwrite)


def get_models():
    """Get abstract models when Django is ready."""
    from .models import get_abstract_models

    return get_abstract_models()


# Package exports
__all__ = [
    # Core classes
    "AppManager",
    # App utilities
    "lemmo_message",
    "success_message",
    "error_message",
    "warning_message",
    "info_message",
    "validate_required_fields",
    "sanitize_data",
    "LemmoResponse",
    "MessageType",
    # Models (use get_models() function to access when Django is ready)
    "get_models",
    # GraphQL Mutations
    "CoreAuthenticatedMutation",
    "CoreUnauthenticatedMutation",
    "MutationError",
    "ValidationError",
    "PermissionError",
    "BusinessLogicError",
    # GraphQL Queries
    "CoreAuthenticatedQuery",
    "CoreUnauthenticatedQuery",
    "PaginatedQuery",
    "FilteredQuery",
    "QueryError",
    "QueryValidationError",
    "QueryPermissionError",
    # Convenience functions
    "get_app_info",
    "get_schema_info",
    "reload_schema",
    "generate_config",
    "get_models",
    # Configuration
    "DEFAULT_APPS",
    "LEMMO_DEFAULT_CONFIG_DATA",
    "get_project_root",
    "get_config_file_path",
    # Version
    "__version__",
    "__author__",
    "__email__",
]
