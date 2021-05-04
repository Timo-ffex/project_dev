from django.shortcuts import render
from rest_framework import generics
from .models import Crop, CropSeason, CropRotation
from .serializers import CropSerializer, CropSeasonSerializer, CropRotationSerializer
from django.core import serializers
from django.http import HttpResponse


##################### Field Serializers ###########################
class ListCrop(generics.ListCreateAPIView):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

class DetailCrop(generics.RetrieveUpdateDestroyAPIView):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer


##################### Activity Serializers ###########################
class ListCropSeason(generics.ListCreateAPIView):
    queryset = CropSeason.objects.all()
    serializer_class = CropSeasonSerializer

class DetailCropSeason(generics.RetrieveUpdateDestroyAPIView):
    queryset = CropSeason.objects.all()
    serializer_class = CropSeasonSerializer


##################### AssignFarmActivity Serializers ###########################
class ListCropRotation(generics.ListCreateAPIView):
    queryset = CropRotation.objects.all()
    serializer_class = CropRotationSerializer


class DetailCropRotation(generics.RetrieveUpdateDestroyAPIView):
    queryset = CropRotation.objects.all()
    serializer_class = CropRotationSerializer
