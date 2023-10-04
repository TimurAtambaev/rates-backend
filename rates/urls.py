"""Модуль путей проекта."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls, name="Admin site"),
    path("api/v1/", include("api.urls"), name="Root url"),
]
