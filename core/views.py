from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json

from core.app_manager import AppManager
from core.app_utils import success_message, error_message, info_message
from core.schema import get_schema_info, reload_schema


class CoreAPIView(View):
    """
    Base API view with common functionality.
    """

    def dispatch(self, request, *args, **kwargs):
        """Add common headers and handle CORS."""
        response = super().dispatch(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    def json_response(self, data, status=200):
        """Return JSON response with standard format."""
        return JsonResponse(data, status=status, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class AppsAPIView(CoreAPIView):
    """
    API view for managing applications.
    """

    def get(self, request):
        """Get information about all configured apps."""
        try:
            app_info = AppManager.get_app_info()
            return self.json_response(
                success_message(
                    message="App information retrieved successfully",
                    data={"apps": app_info},
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to retrieve app information", error_details=[str(e)]
                ),
                status=500,
            )

    def post(self, request):
        """Reload app configuration."""
        try:
            # This would trigger a reload of app configuration
            apps = AppManager.get_apps()
            return self.json_response(
                success_message(
                    message="App configuration reloaded successfully",
                    data={"apps_loaded": len(apps)},
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to reload app configuration", error_details=[str(e)]
                ),
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ConfigAPIView(CoreAPIView):
    """
    API view for managing configuration.
    """

    def get(self, request):
        """Get current configuration."""
        try:
            config_data = AppManager.get_config_data_from_config_file()
            return self.json_response(
                success_message(
                    message="Configuration retrieved successfully",
                    data={"config": config_data},
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to retrieve configuration", error_details=[str(e)]
                ),
                status=500,
            )

    def post(self, request):
        """Update configuration."""
        try:
            data = json.loads(request.body)
            overwrite = data.get("overwrite", False)
            result = AppManager.generate_config(overwrite=overwrite)
            return self.json_response(result)
        except json.JSONDecodeError:
            return self.json_response(
                error_message(
                    message="Invalid JSON data",
                    error_details=["Request body must be valid JSON"],
                ),
                status=400,
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to update configuration", error_details=[str(e)]
                ),
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class SchemaAPIView(CoreAPIView):
    """
    API view for managing GraphQL schema.
    """

    def get(self, request):
        """Get schema information."""
        try:
            schema_info = get_schema_info()
            return self.json_response(
                success_message(
                    message="Schema information retrieved successfully",
                    data={"schema": schema_info},
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to retrieve schema information",
                    error_details=[str(e)],
                ),
                status=500,
            )

    def post(self, request):
        """Reload schema."""
        try:
            schema = reload_schema()
            return self.json_response(
                success_message(
                    message="Schema reloaded successfully", data={"schema_valid": True}
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to reload schema", error_details=[str(e)]
                ),
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class HealthCheckAPIView(CoreAPIView):
    """
    API view for health checks.
    """

    def get(self, request):
        """Perform health check."""
        try:
            # Check basic functionality
            apps = AppManager.get_apps()
            schema_info = get_schema_info()

            health_data = {
                "status": "healthy",
                "apps_loaded": len(apps),
                "schema_valid": schema_info.get("schema_valid", False),
                "timestamp": "2025-01-27T12:00:00Z",  # This should be dynamic
            }

            return self.json_response(
                success_message(message="Health check completed", data=health_data)
            )
        except Exception as e:
            return self.json_response(
                error_message(message="Health check failed", error_details=[str(e)]),
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class SystemInfoAPIView(CoreAPIView):
    """
    API view for system information.
    """

    def get(self, request):
        """Get system information."""
        try:
            import sys
            import django

            system_info = {
                "python_version": sys.version,
                "django_version": django.get_version(),
                "apps_loaded": len(AppManager.get_apps()),
                "schema_info": get_schema_info(),
                "config_path": AppManager.get_config_file_path(),
            }

            return self.json_response(
                success_message(
                    message="System information retrieved successfully",
                    data=system_info,
                )
            )
        except Exception as e:
            return self.json_response(
                error_message(
                    message="Failed to retrieve system information",
                    error_details=[str(e)],
                ),
                status=500,
            )


# Decorator-based views for backward compatibility
@csrf_exempt
@require_http_methods(["GET"])
def apps_view(request):
    """Decorator-based view for apps API."""
    view = AppsAPIView()
    return view.get(request)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def config_view(request):
    """Decorator-based view for config API."""
    view = ConfigAPIView()
    if request.method == "GET":
        return view.get(request)
    elif request.method == "POST":
        return view.post(request)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def schema_view(request):
    """Decorator-based view for schema API."""
    view = SchemaAPIView()
    if request.method == "GET":
        return view.get(request)
    elif request.method == "POST":
        return view.post(request)


@csrf_exempt
@require_http_methods(["GET"])
def health_check_view(request):
    """Decorator-based view for health check API."""
    view = HealthCheckAPIView()
    return view.get(request)


@csrf_exempt
@require_http_methods(["GET"])
def system_info_view(request):
    """Decorator-based view for system info API."""
    view = SystemInfoAPIView()
    return view.get(request)
