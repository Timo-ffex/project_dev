from django.contrib import admin
from .models import Crop, CropSeason, CropRotation

crop_model = [Crop, CropSeason, CropRotation] 
admin.site.register(crop_model)
