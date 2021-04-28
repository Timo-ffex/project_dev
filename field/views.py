from rest_framework import generics
from .models import Field, Season, Activity
from .serializers import FieldSerializer, SeasonSerializer, ActivitySerializer
from django.core import serializers
from django.http import HttpResponse


##################### Field Serializers ###########################
class ListField(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

class DetailField(generics.RetrieveUpdateDestroyAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


##################### Season Serializers ###########################
class ListSeason(generics.ListCreateAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

class DetailSeason(generics.RetrieveUpdateDestroyAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


##################### Activity Serializers ###########################
class ListActivity(generics.ListCreateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class DetailActivity(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


def points(request):
    points = Field.objects.all()
    points_list = serializers.serialize('geojson', points)
    return HttpResponse(points_list, content_type="text/json-comment-filtered")