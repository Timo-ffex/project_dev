from rest_framework import serializers
from .models import Crop, CropSeason, CropRotation


class CropSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Crop
        fields = '__all__'
        # fields = ('id', 'user', 'field_name', 'group_name', 'starting_longitude', 
        #         'starting_latitude', 'ending_longitude', 'ending_latitude', )
    


class CropSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropSeason
        fields = "__all__"


class CropRotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropRotation
        fields = "__all__"
