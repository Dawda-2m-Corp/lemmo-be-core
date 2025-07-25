from django.urls import path, include
from django.views.generic import TemplateView
from .app_manager import AppManager
from .views import (
    AppsAPIView,
    ConfigAPIView,
    SchemaAPIView,
    HealthCheckAPIView,
    SystemInfoAPIView,
    apps_view,
    config_view,
    schema_view,
    health_check_view,
    system_info_view,
)

# Core API URLs
core_api_patterns = [
    path("apps/", AppsAPIView.as_view(), name="core_apps_api"),
    path("config/", ConfigAPIView.as_view(), name="core_config_api"),
    path("schema/", SchemaAPIView.as_view(), name="core_schema_api"),
    path("health/", HealthCheckAPIView.as_view(), name="core_health_api"),
    path("system/", SystemInfoAPIView.as_view(), name="core_system_api"),
]

# Legacy API URLs (decorator-based)
legacy_api_patterns = [
    path("apps/", apps_view, name="core_apps_legacy"),
    path("config/", config_view, name="core_config_legacy"),
    path("schema/", schema_view, name="core_schema_legacy"),
    path("health/", health_check_view, name="core_health_legacy"),
    path("system/", system_info_view, name="core_system_legacy"),
]

# Core URLs
urlpatterns = [
    # API endpoints
    path("api/v1/", include(core_api_patterns)),
    path("api/legacy/", include(legacy_api_patterns)),
    # Documentation
    path(
        "docs/", TemplateView.as_view(template_name="core/docs.html"), name="core_docs"
    ),
    # Status page
    path(
        "status/",
        TemplateView.as_view(template_name="core/status.html"),
        name="core_status",
    ),
]

# Add dynamic app URLs
try:
    app_urls = AppManager.get_app_urls()
    if app_urls:
        urlpatterns.extend(app_urls)
except Exception as e:
    # Log error but don't fail URL loading
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Failed to load app URLs: {e}")
