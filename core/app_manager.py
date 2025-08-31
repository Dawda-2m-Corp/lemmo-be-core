import logging
import yaml
import importlib
import os
from typing import List, Optional, Dict, Any, Tuple
from django.conf import settings
from django.urls import path, include
from core import LEMMO_DEFAULT_CONFIG_DATA
from core.app_utils import error_message, success_message

logger = logging.getLogger(__name__)


class AppManager:
    """Manages application configuration and dynamic module loading for LEMMO."""

    @classmethod
    def get_config_file_path(cls) -> str:
        """
        Safely resolves the config file path using settings.BASE_DIR.
        Falls back to current working directory if BASE_DIR is not available.
        """
        base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        return os.path.join(base_dir, "config.yml")

    @classmethod
    def validate_config_data(
        cls, config_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate configuration data structure.

        Args:
            config_data: Configuration data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not isinstance(config_data, dict):
            errors.append("Configuration must be a dictionary")
            return False, errors

        if "apps" not in config_data:
            errors.append("Configuration must contain 'apps' key")
            return False, errors

        if not isinstance(config_data["apps"], list):
            errors.append("'apps' must be a list")
            return False, errors

        for i, app in enumerate(config_data["apps"]):
            if not isinstance(app, dict):
                errors.append(f"App at index {i} must be a dictionary")
                continue

            required_fields = ["name", "module", "url_prefix"]
            for field in required_fields:
                if field not in app:
                    errors.append(f"App at index {i} missing required field: {field}")
                elif not isinstance(app[field], str):
                    errors.append(f"App at index {i} field '{field}' must be a string")

        return len(errors) == 0, errors

    @classmethod
    def generate_config(cls, overwrite: bool = False) -> Dict[str, Any]:
        """
        Generates the default configuration file at the project root.
        If the file already exists, it will only be overwritten if `overwrite` is True.

        Args:
            overwrite: Whether to overwrite existing config file

        Returns:
            Response message indicating success or failure
        """
        config_path = cls.get_config_file_path()

        if os.path.exists(config_path) and not overwrite:
            logger.warning(
                f"Config file already exists at {config_path}. Skipping generation."
            )
            return error_message(
                message=f"Config file already exists at {config_path}",
                error_details=[f"Use overwrite=True to regenerate"],
            )

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, "w") as config_file:
                yaml.safe_dump(
                    LEMMO_DEFAULT_CONFIG_DATA,
                    config_file,
                    default_flow_style=False,
                    sort_keys=False,
                )
            logger.info(f"Generated config file at {config_path}")
            return success_message(
                message=f"Generated config file at {config_path}",
                data={"config_path": config_path},
            )
        except Exception as e:
            logger.error(f"Failed to generate config file: {e}")
            return error_message(
                message="Failed to generate config file", error_details=[str(e)]
            )

    @classmethod
    def get_config_data_from_config_file(cls) -> Optional[Dict[str, Any]]:
        """
        Loads and returns the configuration data from the config file.
        Returns None on failure.

        Returns:
            Configuration data dictionary or None if failed
        """
        config_path = cls.get_config_file_path()

        try:
            with open(config_path, "r") as config_file:
                config_data = yaml.safe_load(config_file)

            # Validate the loaded configuration
            is_valid, errors = cls.validate_config_data(config_data)
            if not is_valid:
                logger.error(f"Invalid configuration: {errors}")
                return None

            return config_data

        except FileNotFoundError:
            logger.error(f"Config file not found, generating a new one: {config_path}")
            cls.generate_config(overwrite=True)
            # Try to load again after generation
            try:
                with open(config_path, "r") as config_file:
                    return yaml.safe_load(config_file)
            except Exception as e:
                logger.error(f"Failed to load generated config: {e}")
                return None
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

        Returns:
            List of successfully loaded module names
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
                        logger.debug(f"Successfully loaded module: {module_name}")
                except ImportError as e:
                    logger.error(f"Failed to import module '{module_name}': {e}")
                except Exception as e:
                    logger.error(
                        f"Unexpected error loading module '{module_name}': {e}"
                    )
            else:
                logger.warning("Missing 'module' in app definition.")

        logger.info(f"Loaded {len(loaded_modules)} modules: {loaded_modules}")
        return loaded_modules

    @classmethod
    def get_app_schema(cls) -> Tuple[List, List]:
        """
        Get GraphQL queries and mutations from all configured apps.

        Returns:
            Tuple of (queries, mutations) lists
        """
        config_data = cls.get_config_data_from_config_file()
        if not config_data:
            return [], []

        apps = config_data.get("apps", [])

        schema_queries = []
        schema_mutations = []

        for app in apps:
            module_path = app.get("module")

            if module_path:
                try:
                    schema_module = importlib.import_module(f"{module_path}.schema")

                    if schema_module:
                        # Load Query class with validation
                        if hasattr(schema_module, "Query"):
                            query_class = getattr(schema_module, "Query")
                            try:
                                # Validate that it's a proper GraphQL ObjectType
                                if hasattr(query_class, "_meta") and hasattr(
                                    query_class._meta, "fields"
                                ):
                                    # Try to access fields to catch any issues early
                                    try:
                                        fields = query_class._meta.fields
                                        # Check if fields contain any problematic types
                                        for field_name, field in fields.items():
                                            if isinstance(field, dict):
                                                logger.warning(
                                                    f"Skipping Query class from {module_path} - field '{field_name}' is a dict"
                                                )
                                                raise ValueError(
                                                    f"Field '{field_name}' is a dict"
                                                )

                                        schema_queries.append(query_class)
                                        logger.debug(f"Loaded Query from {module_path}")
                                    except Exception as field_error:
                                        logger.error(
                                            f"Error accessing fields in Query class from {module_path}: {field_error}"
                                        )
                                else:
                                    logger.warning(
                                        f"Query class from {module_path} has no _meta.fields"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Error validating Query class from {module_path}: {e}"
                                )

                        # Load Mutation class with validation
                        if hasattr(schema_module, "Mutation"):
                            mutation_class = getattr(schema_module, "Mutation")
                            try:
                                # Validate that it's a proper GraphQL ObjectType
                                if hasattr(mutation_class, "_meta") and hasattr(
                                    mutation_class._meta, "fields"
                                ):
                                    # Try to access fields to catch any issues early
                                    try:
                                        fields = mutation_class._meta.fields
                                        # Check if fields contain any problematic types
                                        for field_name, field in fields.items():
                                            if isinstance(field, dict):
                                                logger.warning(
                                                    f"Skipping Mutation class from {module_path} - field '{field_name}' is a dict"
                                                )
                                                raise ValueError(
                                                    f"Field '{field_name}' is a dict"
                                                )

                                        schema_mutations.append(mutation_class)
                                        logger.debug(
                                            f"Loaded Mutation from {module_path}"
                                        )
                                    except Exception as field_error:
                                        logger.error(
                                            f"Error accessing fields in Mutation class from {module_path}: {field_error}"
                                        )
                                else:
                                    logger.warning(
                                        f"Mutation class from {module_path} has no _meta.fields"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Error validating Mutation class from {module_path}: {e}"
                                )
                except ImportError as ime:
                    logger.warning(
                        f"Cannot import schema module: {module_path}.schema - {ime}"
                    )
                except Exception as e:
                    logger.error(f"Error loading schema from {module_path}: {e}")

        logger.info(
            f"Loaded {len(schema_queries)} queries and {len(schema_mutations)} mutations"
        )
        return schema_queries, schema_mutations

    @classmethod
    def get_app_urls(cls) -> List:
        """
        Returns a list of URL patterns from the loaded apps.
        Each app should define a 'urls' attribute.

        Returns:
            List of URL patterns
        """
        config_data = cls.get_config_data_from_config_file()
        if not config_data:
            return []

        apps = config_data.get("apps", [])
        urls = []

        for app in apps:
            try:
                url_module = importlib.import_module(f"{app['module']}.urls")

                if hasattr(url_module, "urlpatterns"):
                    try:
                        # Try to access urlpatterns to validate they're accessible
                        urlpatterns = getattr(url_module, "urlpatterns")

                        # If we get here, urlpatterns exist and are accessible
                        url_prefix = app.get("url_prefix", "")
                        urls.extend(path(f"{url_prefix}/", include(url_module)))
                        logger.debug(
                            f"Loaded URLs for {app['name']} with prefix: {url_prefix}"
                        )
                    except AttributeError as e:
                        logger.warning(
                            f"App {app['name']} has urlpatterns but they're not accessible: {e}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"App {app['name']} has urlpatterns but there's an error: {e}"
                        )
                else:
                    logger.warning(
                        f"App {app['name']} does not have a 'urlpatterns' attribute."
                    )
            except ImportError as e:
                logger.warning(f"App {app['name']} does not have a urls.py file: {e}")
            except Exception as e:
                logger.error(
                    f"Unexpected error loading URLs for app '{app['name']}': {e}"
                )

        logger.info(f"Loaded URL patterns from {len(urls)} apps")
        return urls

    @classmethod
    def _validate_module(cls, module_name: str) -> bool:
        """
        Checks if the module can be successfully imported using importlib.

        Args:
            module_name: Name of the module to validate

        Returns:
            True if module can be imported, False otherwise
        """
        try:
            importlib.import_module(module_name)
            return True
        except ImportError as e:
            logger.error(f"Module '{module_name}' could not be imported: {e}")
            return False

    @classmethod
    def get_app_info(cls) -> List[Dict[str, Any]]:
        """
        Get detailed information about all configured apps.

        Returns:
            List of app information dictionaries
        """
        config_data = cls.get_config_data_from_config_file()
        if not config_data:
            return []

        apps = config_data.get("apps", [])
        app_info = []

        for app in apps:
            info = {
                "name": app.get("name", "Unknown"),
                "description": app.get("description", ""),
                "module": app.get("module", ""),
                "url_prefix": app.get("url_prefix", ""),
                "is_loaded": cls._validate_module(app.get("module", "")),
                "has_schema": False,
                "has_urls": False,
            }

            # Check if module has schema
            if info["module"]:
                try:
                    schema_module = importlib.import_module(f"{info['module']}.schema")
                    info["has_schema"] = hasattr(schema_module, "Query") or hasattr(
                        schema_module, "Mutation"
                    )
                except ImportError:
                    pass

            # Check if module has URLs - with better error handling
            if info["module"]:
                try:
                    url_module = importlib.import_module(f"{info['module']}.urls")
                    info["has_urls"] = hasattr(url_module, "urlpatterns")

                    # Additional validation: check if urlpatterns can be accessed without errors
                    if info["has_urls"]:
                        try:
                            # Try to access urlpatterns to catch any AttributeError
                            # But don't fail the entire process if there are issues
                            urlpatterns = getattr(url_module, "urlpatterns")
                            # If we get here, the urlpatterns exist and are accessible
                        except AttributeError as e:
                            logger.warning(
                                f"App {info['name']} has urlpatterns but they're not accessible: {e}"
                            )
                            info["has_urls"] = False
                        except Exception as e:
                            logger.warning(
                                f"App {info['name']} has urlpatterns but there's an error: {e}"
                            )
                            info["has_urls"] = False

                except ImportError:
                    # Module doesn't have urls.py - this is normal for some apps
                    pass
                except AttributeError as e:
                    # Handle AttributeError during import (e.g., missing view classes)
                    logger.warning(
                        f"App {info['name']} has urls.py but import failed due to missing components: {e}"
                    )
                    info["has_urls"] = False
                except Exception as e:
                    # Catch any other exceptions during URL validation
                    logger.warning(f"Error checking URLs for app {info['name']}: {e}")
                    info["has_urls"] = False

            app_info.append(info)

        return app_info
