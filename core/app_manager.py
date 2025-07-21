import logging
import yaml
import importlib
import os
from typing import List, Optional, Dict, Any
from django.conf import settings
from core import LEMMO_DEFAULT_CONFIG_DATA
from django.urls import path, include

logger = logging.getLogger(__name__)


class AppManager:
    """Manages application configuration and dynamic module loading for LEMMO."""

    @classmethod
    def get_config_file_path(cls) -> str:
        """
        Safely resolves the config file path using settings.BASE_DIR.
        """
        base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        return os.path.join(base_dir, "config.yml")

    @classmethod
    def generate_config(cls, overwrite: bool = False) -> bool:
        """
        Generates the default configuration file at the project root.
        If the file already exists, it will only be overwritten if `overwrite` is True.
        Returns True if the file was created or overwritten, False otherwise.
        """
        config_path = cls.get_config_file_path()

        if os.path.exists(config_path) and not overwrite:
            logger.warning(
                f"Config file already exists at {config_path}. Skipping generation."
            )
            return False

        try:
            with open(config_path, "w") as config_file:
                yaml.safe_dump(
                    LEMMO_DEFAULT_CONFIG_DATA, config_file, default_flow_style=False
                )
            logger.info(f"Generated config file at {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate config file: {e}")
            return False

    @classmethod
    def get_config_data_from_config_file(cls) -> Optional[Dict[str, Any]]:
        """
        Loads and returns the configuration data from the config file.
        Returns None on failure.
        """
        config_path = cls.get_config_file_path()

        try:
            with open(config_path, "r") as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            logger.error(f"Config file not found, generating a new one: {config_path}")
            cls.generate_config(overwrite=True)
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading config: {e}")
        return None

    @classmethod
    def get_apps(cls) -> List[str]:
        """
        Extracts and dynamically imports app modules listed in the configuration.
        Returns a list of successfully loaded modules.
        """
        config_data = cls.get_config_data_from_config_file()
        if not isinstance(config_data, dict):
            logger.error("Invalid or missing configuration data.")
            return []

        apps = config_data.get("apps", [])
        loaded_modules = []

        for app in apps:
            module_name = app.get("module")
            if module_name:
                try:
                    module = importlib.import_module(module_name)
                    if module:
                        loaded_modules.append(module_name)
                except ImportError as e:
                    logger.error(f"Failed to import module '{module_name}': {e}")
            else:
                logger.warning("Missing 'module' in app definition.")
        return loaded_modules

    @classmethod
    def get_app_schema(cls):
        config_data = cls.get_config_data_from_config_file()
        apps = config_data.get("apps", [])

        schema_queries = []
        schema_mutations = []

        for app in apps:
            module_path = app["module"]

            if module_path:
                try:
                    schema_module = importlib.import_module(f"{module_path}.schema")

                    if schema_module:
                        if hasattr(schema_module, "Query"):
                            schema_queries.append(getattr(schema_module, "Query"))
                        if hasattr(schema_module, "Mutation"):
                            schema_mutations.append(getattr(schema_module, "Mutation"))
                except ImportError as ime:
                    logger.warning(
                        f"Cannot import module: {module_path} to load Queries and Mutations: {ime}"
                    )

        return schema_queries, schema_mutations

    @classmethod
    def get_app_urls(cls) -> List[str]:
        """
        Returns a list of URLs from the loaded apps.
        Each app should define a 'urls' attribute.

        """
        config_data = cls.get_config_data_from_config_file()
        apps = config_data.get("apps", [])
        urls = []

        for app in apps:
            try:
                url_module = importlib.import_module(f"{app['module']}.urls")

                if hasattr(url_module, "urlpatterns"):
                    urls.extend(path(f"{app['url_prefix']}/", include(url_module)))
                else:
                    logger.warning(f"App {app} does not have a 'urls' attribute.")
            except ImportError as e:
                logger.error(f"Failed to import URLs for app '{app['name']}': {e}")
        return urls

    @classmethod
    def _validate_module(cls, module_name: str) -> bool:
        """
        Checks if the module can be successfully imported using importlib.
        """
        try:
            importlib.import_module(module_name)
            return True
        except ImportError as e:
            logger.error(f"Module '{module_name}' could not be imported: {e}")
            return False
