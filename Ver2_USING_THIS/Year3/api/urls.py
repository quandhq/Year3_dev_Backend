from django.urls import path
from api import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('v1.1/monitor/data', views.getSensorSecondlyData),
    path('v1.1/monitor/data/history', views.historyChart),
    path('get/kriging', views.kriging),
    path('v1.1/control/fans',views.send_setpoint), #view to send setpoint to gateway
    path('get/test_authentication', views.getAuthenticationSensorSecondlyData),
    path('get/token_auth', obtain_auth_token), #api to get token authentication
    path('token', TokenObtainPairView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('token/verify', TokenVerifyView.as_view()),
]
