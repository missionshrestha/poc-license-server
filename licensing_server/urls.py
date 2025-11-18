# licensing_server/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/licenses/", include("licenses.urls")),
]
