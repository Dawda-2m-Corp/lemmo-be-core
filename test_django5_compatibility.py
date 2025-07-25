#!/usr/bin/env python3
"""
Test script to verify Django 5.0 compatibility.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for Django 5.0
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
        # Django 5.0 specific settings
        USE_TZ=True,
        TIME_ZONE="UTC",
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
    )
    django.setup()

from core import AppManager, get_schema_info
from core.schema import create_schema, schema
from core.app_utils import (
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


def test_django_version():
    """Test that Django 5.0+ is being used."""
    print("=== Testing Django Version ===")

    import django

    django_version = django.get_version()
    print(f"Django version: {django_version}")

    # Check if it's Django 5.0 or higher
    version_parts = django_version.split(".")
    major_version = int(version_parts[0])
    minor_version = int(version_parts[1])

    if major_version >= 5:
        print("✅ Django 5.0+ detected")
    else:
        print(f"❌ Expected Django 5.0+, got {django_version}")
        return False

    return True


def test_core_imports():
    """Test that all core imports work with Django 5.0."""
    print("\n=== Testing Core Imports ===")

    try:
        # Test app manager
        apps = AppManager.get_apps()
        print(f"✅ AppManager.get_apps() works: {len(apps)} apps")

        # Test schema
        schema_info = get_schema_info()
        print(f"✅ get_schema_info() works: {schema_info}")

        # Test app utilities
        result = lemmo_message(success=True, message="Test")
        print(f"✅ lemmo_message() works: {result['success']}")

        success = success_message("Test", {"data": "test"})
        print(f"✅ success_message() works: {success['success']}")

        error = error_message("Test", ["error"])
        print(f"✅ error_message() works: {not error['success']}")

        warning = warning_message("Test", {"warning": "test"})
        print(f"✅ warning_message() works: {warning['success']}")

        info = info_message("Test", {"info": "test"})
        print(f"✅ info_message() works: {info['success']}")

        # Test validation functions
        data = {"field1": "value1", "field2": "value2"}
        missing = validate_required_fields(data, ["field1", "field3"])
        print(f"✅ validate_required_fields() works: {missing}")

        sanitized = sanitize_data(data, ["field1"])
        print(f"✅ sanitize_data() works: {sanitized}")

        # Test response dataclass
        response = LemmoResponse(
            success=True,
            message="Test",
            data={"test": "data"},
            message_type=MessageType.SUCCESS,
        )
        print(f"✅ LemmoResponse works: {response.success}")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_schema_creation():
    """Test that schema creation works with Django 5.0."""
    print("\n=== Testing Schema Creation ===")

    try:
        # Create fresh schema
        fresh_schema = create_schema()
        print(f"✅ Schema creation works: {type(fresh_schema)}")

        # Check query type
        query_type = fresh_schema.get_query_type()
        if query_type:
            fields = list(query_type.fields.keys())
            print(f"✅ Query fields available: {fields}")
        else:
            print("❌ No query type found")
            return False

        # Check mutation type
        mutation_type = fresh_schema.get_mutation_type()
        if mutation_type:
            fields = list(mutation_type.fields.keys())
            print(f"✅ Mutation fields available: {fields}")
        else:
            print("ℹ️ No mutation type found (this is normal for empty schema)")

        return True

    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_app_manager():
    """Test app manager functionality with Django 5.0."""
    print("\n=== Testing App Manager ===")

    try:
        # Generate config
        result = AppManager.generate_config(overwrite=True)
        print(f"✅ Config generation: {result['success']}")

        # Get app info
        app_info = AppManager.get_app_info()
        print(f"✅ App info: {len(app_info)} apps configured")

        # Get schema components
        queries, mutations = AppManager.get_app_schema()
        print(
            f"✅ Schema components: {len(queries)} queries, {len(mutations)} mutations"
        )

        return True

    except Exception as e:
        print(f"❌ App manager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all Django 5.0 compatibility tests."""
    print("Lemmo Core - Django 5.0 Compatibility Test")
    print("=" * 50)

    tests = [
        test_django_version,
        test_core_imports,
        test_schema_creation,
        test_app_manager,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! Django 5.0 compatibility confirmed.")
    else:
        print("❌ Some tests failed. Please check the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
