from django.urls import path

from monitoring.views import analyze_anomaly, dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/analyze-anomaly/", analyze_anomaly, name="analyze_anomaly"),
]
