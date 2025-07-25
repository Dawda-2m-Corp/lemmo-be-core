#!/usr/bin/env python3
"""
Diagnostic script to identify schema loading issues.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "core",
        ],
        SECRET_KEY="test-secret-key",
        BASE_DIR=os.path.dirname(os.path.abspath(__file__)),
    )
    django.setup()

import importlib
import logging
from core import AppManager

# Set up logging to see detailed output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def inspect_query_class(module_path):
    """Inspect a specific Query class to identify issues."""
    print(f"\n=== Inspecting Query class from {module_path} ===")

    try:
        # Try to import the schema module
        schema_module = importlib.import_module(f"{module_path}.schema")
        print(f"✅ Successfully imported {module_path}.schema")

        if hasattr(schema_module, "Query"):
            query_class = getattr(schema_module, "Query")
            print(f"✅ Found Query class: {query_class}")
            print(f"   Class name: {query_class.__name__}")
            print(f"   Module: {query_class.__module__}")

            # Check if it has _meta
            if hasattr(query_class, "_meta"):
                print(f"✅ Query class has _meta")

                # Check if it has fields
                if hasattr(query_class._meta, "fields"):
                    fields = query_class._meta.fields
                    print(f"✅ Query class has {len(fields)} fields")

                    # Inspect each field
                    for field_name, field in fields.items():
                        print(f"   Field: {field_name}")
                        print(f"     Type: {type(field)}")
                        print(f"     Has 'type' attr: {hasattr(field, 'type')}")
                        print(f"     Has '_type' attr: {hasattr(field, '_type')}")

                        # Check if it's a dict (which would cause the error)
                        if isinstance(field, dict):
                            print(
                                f"     ⚠️  WARNING: Field is a dict! This will cause issues."
                            )
                            print(f"     Dict content: {field}")
                        elif hasattr(field, "type") or hasattr(field, "_type"):
                            print(f"     ✅ Field appears to be a valid GraphQL field")
                        else:
                            print(
                                f"     ⚠️  Field doesn't have expected GraphQL field attributes"
                            )
                else:
                    print(f"❌ Query class has no _meta.fields")
            else:
                print(f"❌ Query class has no _meta")
        else:
            print(f"❌ No Query class found in {module_path}.schema")

    except ImportError as e:
        print(f"❌ Cannot import {module_path}.schema: {e}")
    except Exception as e:
        print(f"❌ Error inspecting {module_path}: {e}")
        import traceback

        traceback.print_exc()


def test_schema_loading():
    """Test the schema loading process with detailed logging."""
    print("\n=== Testing Schema Loading ===")

    try:
        # Get schema components
        queries, mutations = AppManager.get_app_schema()
        print(f"✅ Loaded {len(queries)} queries and {len(mutations)} mutations")

        # Inspect each query class
        for i, query_class in enumerate(queries):
            print(f"\n--- Query {i + 1} ---")
            print(f"Class: {query_class}")
            print(f"Name: {query_class.__name__}")
            print(f"Module: {query_class.__module__}")

            if hasattr(query_class, "_meta") and hasattr(query_class._meta, "fields"):
                fields = query_class._meta.fields
                print(f"Fields: {list(fields.keys())}")

                # Check for problematic fields
                for field_name, field in fields.items():
                    if isinstance(field, dict):
                        print(f"⚠️  PROBLEMATIC FIELD: {field_name} is a dict!")
                        print(f"    Dict content: {field}")
                    elif not (hasattr(field, "type") or hasattr(field, "_type")):
                        print(
                            f"⚠️  SUSPICIOUS FIELD: {field_name} doesn't look like a GraphQL field"
                        )
                        print(f"    Field type: {type(field)}")
            else:
                print("❌ Query class has no _meta.fields")

    except Exception as e:
        print(f"❌ Error in schema loading: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run the diagnostic."""
    print("Lemmo Core - Schema Loading Diagnostic")
    print("=" * 50)

    # Get app info
    app_info = AppManager.get_app_info()
    print(f"Configured apps: {len(app_info)}")

    for app in app_info:
        print(f"  - {app['name']}: {app['module']} (loaded: {app['is_loaded']})")

    # Test specific problematic app
    inspect_query_class("lemmo_apps.authentication")

    # Test general schema loading
    test_schema_loading()

    print("\n" + "=" * 50)
    print("Diagnostic complete!")


if __name__ == "__main__":
    main()
