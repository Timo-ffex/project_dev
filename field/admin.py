from django.contrib import admin
from .models import Field, Activity, AssignFarmActivity

field_model = [Field, Activity, AssignFarmActivity] 
admin.site.register(field_model)
