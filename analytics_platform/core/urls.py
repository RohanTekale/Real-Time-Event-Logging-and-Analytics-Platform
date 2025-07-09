from django.urls import path
from analytics_platform.core import views
from rest_framework_simplejwt.views import TokenRefreshView
from .utils import CustomTokenObtainPairView
app_name = 'core'

urlpatterns = [
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/users/', views.UserCreateView.as_view(), name='user_create'),
    path('api/auth/permission/', views.PermissionView.as_view(), name='permissions'),
    path('api/events/', views.EventSubmitView.as_view(), name='event_submit'),
    path('api/analytics/metrics/', views.AnalyticsMetricsView.as_view(), name='analytics_metrics'),
    path('api/analytics/events/', views.EventAnalyticsView.as_view(), name='event_analytics'),
    path('api/analytics/ml-insights/', views. MLinsigthsView.as_view(), name='ml_insights'),
    path('api/analytics/anomaly-detection/', views.AnomalyDetectionView.as_view(), name='anomaly_detection'),
    path('api/analytics/predictions/', views.TrafficPredictionView.as_view(), name='predictions'),
    path('api/monitoring/health/', views.SystemHealthView.as_view(), name='system_health'),
    path('api/monitoring/containers/', views.ContainerStatusView.as_view(), name='container_status'),
]