from django.contrib import admin
from .models import Field, Season, Activity

field_model = [Field, Season, Activity] 
admin.site.register(field_model)
