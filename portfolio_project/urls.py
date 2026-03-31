"""URL configuration for the portfolio Django project."""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
  path("admin/", admin.site.urls),
  path("", include("siteapp.urls")),
]
