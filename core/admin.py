from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from core.app_manager import AppManager
from core.app_utils import success_message, error_message


class LemmoAdminSite(AdminSite):
    """
    Custom admin site for Lemmo with additional functionality.
    """

    site_header = "Lemmo Administration"
    site_title = "Lemmo Admin"
    index_title = "Welcome to Lemmo Administration"

    def get_urls(self):
        """Add custom URLs to admin site."""
        urls = super().get_urls()
        custom_urls = [
            path("api/apps/", self.admin_view(self.apps_api_view), name="apps_api"),
            path(
                "api/config/", self.admin_view(self.config_api_view), name="config_api"
            ),
            path(
                "api/schema/", self.admin_view(self.schema_api_view), name="schema_api"
            ),
        ]
        return custom_urls + urls

    def apps_api_view(self, request):
        """API endpoint to get app information."""
        try:
            app_info = AppManager.get_app_info()
            return JsonResponse(
                success_message(
                    message="App information retrieved successfully",
                    data={"apps": app_info},
                )
            )
        except Exception as e:
            return JsonResponse(
                error_message(
                    message="Failed to retrieve app information", error_details=[str(e)]
                )
            )

    def config_api_view(self, request):
        """API endpoint to manage configuration."""
        if request.method == "GET":
            try:
                config_data = AppManager.get_config_data_from_config_file()
                return JsonResponse(
                    success_message(
                        message="Configuration retrieved successfully",
                        data={"config": config_data},
                    )
                )
            except Exception as e:
                return JsonResponse(
                    error_message(
                        message="Failed to retrieve configuration",
                        error_details=[str(e)],
                    )
                )
        elif request.method == "POST":
            try:
                data = json.loads(request.body)
                overwrite = data.get("overwrite", False)
                result = AppManager.generate_config(overwrite=overwrite)
                return JsonResponse(result)
            except Exception as e:
                return JsonResponse(
                    error_message(
                        message="Failed to update configuration", error_details=[str(e)]
                    )
                )

    def schema_api_view(self, request):
        """API endpoint to get schema information."""
        try:
            from core.schema import get_schema_info

            schema_info = get_schema_info()
            return JsonResponse(
                success_message(
                    message="Schema information retrieved successfully",
                    data={"schema": schema_info},
                )
            )
        except Exception as e:
            return JsonResponse(
                error_message(
                    message="Failed to retrieve schema information",
                    error_details=[str(e)],
                )
            )


# Create custom admin site instance
lemmo_admin_site = LemmoAdminSite(name="lemmo_admin")


class CoreAdminMixin:
    """
    Mixin for admin classes with common functionality.
    """

    def get_readonly_fields(self, request, obj=None):
        """Add common readonly fields."""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if hasattr(self.model, "created_at"):
            readonly_fields.append("created_at")
        if hasattr(self.model, "updated_at"):
            readonly_fields.append("updated_at")
        if hasattr(self.model, "id"):
            readonly_fields.append("id")
        return readonly_fields

    def get_list_display(self, request):
        """Add common list display fields."""
        list_display = list(super().get_list_display(request))
        if hasattr(self.model, "created_at") and "created_at" not in list_display:
            list_display.append("created_at")
        return list_display

    def get_list_filter(self, request):
        """Add common list filters."""
        list_filter = list(super().get_list_filter(request))
        if hasattr(self.model, "created_at"):
            list_filter.append("created_at")
        if hasattr(self.model, "status"):
            list_filter.append("status")
        return list_filter

    def get_search_fields(self, request):
        """Add common search fields."""
        search_fields = list(super().get_search_fields(request))
        if hasattr(self.model, "name"):
            search_fields.append("name")
        if hasattr(self.model, "code"):
            search_fields.append("code")
        return search_fields


class UUIDModelAdmin(CoreAdminMixin, admin.ModelAdmin):
    """
    Admin class for models with UUID primary key.
    """

    def get_readonly_fields(self, request, obj=None):
        """Make UUID field readonly."""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.append("id")
        return readonly_fields


class TimeDataStampedModelAdmin(CoreAdminMixin, admin.ModelAdmin):
    """
    Admin class for models with timestamps.
    """

    def get_readonly_fields(self, request, obj=None):
        """Make timestamp fields readonly."""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.extend(["created_at", "updated_at"])
        return readonly_fields

    def get_list_display(self, request):
        """Add timestamp to list display."""
        list_display = list(super().get_list_display(request))
        list_display.extend(["created_at", "updated_at"])
        return list_display


class SoftDeleteModelAdmin(CoreAdminMixin, admin.ModelAdmin):
    """
    Admin class for models with soft delete functionality.
    """

    def get_queryset(self, request):
        """Filter out soft-deleted objects by default."""
        qs = super().get_queryset(request)
        if hasattr(qs.model, "is_deleted"):
            return qs.filter(is_deleted=False)
        return qs

    def get_list_display(self, request):
        """Add deletion status to list display."""
        list_display = list(super().get_list_display(request))
        if hasattr(self.model, "is_deleted"):
            list_display.append("is_deleted")
        return list_display

    def get_list_filter(self, request):
        """Add deletion status filter."""
        list_filter = list(super().get_list_filter(request))
        if hasattr(self.model, "is_deleted"):
            list_filter.append("is_deleted")
        return list_filter


class StatusModelAdmin(CoreAdminMixin, admin.ModelAdmin):
    """
    Admin class for models with status field.
    """

    def get_list_display(self, request):
        """Add status to list display."""
        list_display = list(super().get_list_display(request))
        if hasattr(self.model, "status"):
            list_display.append("status")
        return list_display

    def get_list_filter(self, request):
        """Add status filter."""
        list_filter = list(super().get_list_filter(request))
        if hasattr(self.model, "status"):
            list_filter.append("status")
        return list_filter


# Register the core admin site
admin.site = lemmo_admin_site
