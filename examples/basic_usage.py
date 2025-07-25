#!/usr/bin/env python3
"""
Basic usage example for the Lemmo Core package.

This example demonstrates how to use the core package features.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        SECRET_KEY="example-secret-key",
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    django.setup()

from django.db import models
import graphene
from core import (
    AppManager,
    lemmo_message,
    success_message,
    error_message,
    get_models,
    CoreAuthenticatedMutation,
)


def example_app_utils():
    """Demonstrate app utilities usage."""
    print("=== App Utilities Example ===")

    # Basic message
    result = lemmo_message(
        success=True,
        message="Operation completed successfully",
        data={"user_id": "123", "status": "active"},
    )
    print(f"Basic message: {result}")

    # Success message helper
    success = success_message("User created", {"id": "456"})
    print(f"Success message: {success}")

    # Error message helper
    error = error_message("Validation failed", ["Email is required"])
    print(f"Error message: {error}")


def example_app_manager():
    """Demonstrate app manager usage."""
    print("\n=== App Manager Example ===")

    # Generate configuration
    result = AppManager.generate_config(overwrite=True)
    print(f"Config generation: {result}")

    # Get app information
    app_info = AppManager.get_app_info()
    print(f"App info: {len(app_info)} apps configured")

    # Get loaded apps
    apps = AppManager.get_apps()
    print(f"Loaded apps: {apps}")


def example_models():
    """Demonstrate model usage."""
    print("\n=== Models Example ===")

    # Get models when Django is ready
    models = get_models()
    TimeDataStampedModel = models["TimeDataStampedModel"]

    # Create a simple model class
    class ExampleModel(TimeDataStampedModel):
        name = models.CharField(max_length=100)
        description = models.TextField(blank=True)

        class Meta:
            app_label = "core"

    # Create an instance (in a real app, this would be saved to database)
    model = ExampleModel()
    model.name = "Example Model"
    model.description = "This is an example model"

    print(f"Model: {model}")
    print(f"Model ID: {model.id}")
    print(f"Created at: {model.created_at}")
    print(f"Updated at: {model.updated_at}")


def example_graphql_mutation():
    """Demonstrate GraphQL mutation usage."""
    print("\n=== GraphQL Mutation Example ===")

    # Create a simple mutation
    class CreateUserMutation(CoreAuthenticatedMutation):
        class Arguments:
            name = graphene.String(required=True)
            email = graphene.String(required=True)

        @classmethod
        def perform_mutation(cls, root, info, user, name, email):
            # In a real app, you would create the user here
            user_data = {
                "id": "user-123",
                "name": name,
                "email": email,
                "created_by": user.username if user else "system",
            }

            return success_message(
                message="User created successfully", data={"user": user_data}
            )

    print("Mutation class created successfully")
    print("In a real GraphQL schema, this would be registered")


def example_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Example ===")

    # Get configuration data
    config_data = AppManager.get_config_data_from_config_file()
    if config_data:
        apps = config_data.get("apps", [])
        print(f"Configuration loaded: {len(apps)} apps configured")

        for app in apps:
            print(f"  - {app['name']}: {app['module']}")
    else:
        print("No configuration found")


def main():
    """Run all examples."""
    print("Lemmo Core Package - Basic Usage Examples")
    print("=" * 50)

    try:
        example_app_utils()
        example_app_manager()
        example_models()
        example_graphql_mutation()
        example_configuration()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
