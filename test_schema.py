#!/usr/bin/env python3
"""
Test script to verify GraphQL schema creation and query visibility.
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

from core import AppManager, get_schema_info
from core.schema import create_schema, schema


def test_schema_creation():
    """Test that the schema is created properly with all queries."""
    print("=== Testing Schema Creation ===")

    # Get schema info
    info = get_schema_info()
    print(f"Schema info: {info}")

    # Create a fresh schema
    fresh_schema = create_schema()
    print(f"Fresh schema created: {type(fresh_schema)}")

    # Check if the schema has the hello query
    query_type = fresh_schema.get_query_type()
    if query_type:
        fields = query_type.fields
        print(f"Query fields: {list(fields.keys())}")

        if "hello" in fields:
            print("✅ Hello query is present in schema")
        else:
            print("❌ Hello query is missing from schema")
    else:
        print("❌ No query type found in schema")


def test_app_manager():
    """Test app manager functionality."""
    print("\n=== Testing App Manager ===")

    # Generate config
    result = AppManager.generate_config(overwrite=True)
    print(f"Config generation: {result}")

    # Get app info
    app_info = AppManager.get_app_info()
    print(f"App info: {len(app_info)} apps configured")

    for app in app_info:
        print(
            f"  - {app['name']}: {app['module']} (loaded: {app['is_loaded']}, has_schema: {app['has_schema']})"
        )

    # Get schema components
    queries, mutations = AppManager.get_app_schema()
    print(f"Found {len(queries)} queries and {len(mutations)} mutations")


def test_schema_fields():
    """Test that schema fields are properly accessible."""
    print("\n=== Testing Schema Fields ===")

    # Get the current schema
    current_schema = schema

    # Check query type
    query_type = current_schema.get_query_type()
    if query_type:
        fields = query_type.fields
        print(f"Available query fields: {list(fields.keys())}")

        # Test introspection
        for field_name, field in fields.items():
            print(f"  - {field_name}: {type(field.type)}")
    else:
        print("❌ No query type found")

    # Check mutation type
    mutation_type = current_schema.get_mutation_type()
    if mutation_type:
        fields = mutation_type.fields
        print(f"Available mutation fields: {list(fields.keys())}")
    else:
        print("No mutation type found")


def main():
    """Run all tests."""
    print("Lemmo Core - GraphQL Schema Test")
    print("=" * 40)

    try:
        test_app_manager()
        test_schema_creation()
        test_schema_fields()

        print("\n" + "=" * 40)
        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
