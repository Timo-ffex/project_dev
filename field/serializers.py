from rest_framework import serializers
from .models import Field, Activity, AssignFarmActivity


class FieldSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Field
        fields = '__all__'
        # fields = ('id', 'user', 'field_name', 'group_name', 'starting_longitude', 
        #         'starting_latitude', 'ending_longitude', 'ending_latitude', )
    


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class AssignFarmActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignFarmActivity
        fields = "__all__"


# class CoordinateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Field
#         fields = '__all__'