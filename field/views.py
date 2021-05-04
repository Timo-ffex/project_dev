from rest_framework import generics
from .models import Field, Activity, AssignFarmActivity
from .serializers import FieldSerializer, ActivitySerializer, AssignFarmActivitySerializer
from django.core import serializers
from django.http import HttpResponse


##################### Field Serializers ###########################
class ListField(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

class DetailField(generics.RetrieveUpdateDestroyAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


##################### Activity Serializers ###########################
class ListActivity(generics.ListCreateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class DetailActivity(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


##################### AssignFarmActivity Serializers ###########################
class ListSeason(generics.ListCreateAPIView):
    queryset = AssignFarmActivity.objects.all()
    serializer_class = AssignFarmActivitySerializer

class DetailSeason(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssignFarmActivity.objects.all()
    serializer_class = AssignFarmActivitySerializer



# def points(request):
#     points = Field.objects.all()
#     points_list = serializers.serialize('geojson', points)
#     return HttpResponse(points_list, content_type="text/json-comment-filtered")