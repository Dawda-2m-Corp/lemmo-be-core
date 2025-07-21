from django.urls import path
from .app_manager import AppManager

urlpatterns = []

urlpatterns += AppManager.get_app_urls()
