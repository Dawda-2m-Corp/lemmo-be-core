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
    }
]

LEMMO_DEFAULT_CONFIG_DATA = {
    "apps": DEFAULT_APPS,
}
