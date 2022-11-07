from urllib import request
from django.shortcuts import render
from django import http
from rest_framework import mixins
from rest_framework import generics
from api import models
from api import serializers


# Create your views here.


class SensorMixinView(mixins.ListModelMixin,
                        generics.GenericAPIView):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   queryset = models.Sensor.objects.order_by('time') [:15]
   serializer_class = serializers.SensorSerializer
   def get(self, request , *args, **kwargs):
      print(args,kwargs)
      return self.list(request, *args, **kwargs)
   
def index(request):
   mydata = models.Sensor.objects.all().values()
   print(mydata[0])
   context = {
    'insert_me': mydata,
   }		
   #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA

   return render(request, "api\main.html", context=context)
