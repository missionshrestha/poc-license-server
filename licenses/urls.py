# licenses/urls.py

from django.urls import path

from .views import IssueLicenseView, DownloadLicenseView

urlpatterns = [
    path("issue/", IssueLicenseView.as_view(), name="license-issue"),
    path("<str:license_id>/download/", DownloadLicenseView.as_view(), name="license-download"),
]
