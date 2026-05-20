from django.urls import path

from monitoring.views import dashboard, telemetry_proxy

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/telemetry/", telemetry_proxy, name="telemetry_proxy"),
]
