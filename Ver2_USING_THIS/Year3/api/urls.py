from django.urls import path
from api import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    # path('get/<int:year>/<int:month>/<slug:slug>/', views.SensorMixinView.as_view()),
    path('get/secondly_data/<int:id>', views.getSensorSecondlyData),
    path('get/daily_data/<int:id>', views.getSensorDailyData),
    path('get/index', views.index, name="_get_index"),
    path('get/kriging', views.kriging),
    path('set/<int:param>', views.send_set_point), #view to send setpoint to sensor
    path('get/test_authentication', views.getAuthentaicationSensorSecondlyData),
    path('get/token_auth', obtain_auth_token), #api to get token authentication
    path('token', TokenObtainPairView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('token/verify', TokenVerifyView.as_view()),
    #_________testing url_____________
    path('get/test_redirect', views.test_redirect),
]
