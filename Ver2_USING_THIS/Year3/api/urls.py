from django.urls import path
from api import views

urlpatterns = [
    # path('get/<int:year>/<int:month>/<slug:slug>/', views.SensorMixinView.as_view()),
    path('get/secondly_data/<int:id>', views.SensorSecondlyData.as_view()),
    path('get/daily_data/<int:id>', views.SensorDailyData.as_view()),
    path('get/index/', views.index),
    path('get/kriging', views.kriging),
    path('set/<int:param>', views.send_set_point), #view to send setpoint to sensor
]
