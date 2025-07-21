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
    }
]

LEMMO_DEFAULT_CONFIG_DATA = {
    "apps": DEFAULT_APPS,
}
