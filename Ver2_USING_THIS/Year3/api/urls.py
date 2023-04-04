from django.urls import path
from api import views

urlpatterns = [
    # path('get/<int:year>/<int:month>/<slug:slug>/', views.SensorMixinView.as_view()),
    path('get/<int:id>', views.SensorMixinView.as_view()),
    path('get/index/', views.index),
    path('get/kriging', views.kriging),
    path('set/<int:param>', views.send_set_point), #view to send setpoint to sensor
]
