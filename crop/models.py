from django.db import models
from field.models import Field, year_choices, current_year
from django.contrib.auth.models import Group, User
import datetime



class Crop(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    crop_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('field', 'crop_name',)

    def __str__(self):
        return self.crop_name 


class CropSeason(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    crop_name = models.ForeignKey(Crop, on_delete=models.CASCADE)
    crop_description = models.TextField()
    sowing_date = models.DateField(default=datetime.date.today, null=False)
    season = models.IntegerField(('year'), choices=year_choices(), default=current_year)

    def __str__(self):
        return self.season



class CropRotation(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    crop_name = models.ForeignKey(Crop, on_delete=models.CASCADE)
    season = models.ForeignKey(CropSeason, on_delete=models.CASCADE)
    sowing_date = models.DateField(default=datetime.date.today)


# class Activity(models.Model):
#     field = models.ForeignKey(Field, on_delete=models.CASCADE)
#     activity_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
#     activity_type = models.CharField(max_length=100, blank=False, null=False)
#     description = models.TextField(null=False)
#     actual_cost = models.DecimalField(max_digits=9, decimal_places=6, null=False)
#     planned_cost = models.DecimalField(max_digits=9, decimal_places=6, null=False)
#     start_date = models.DateField(default=datetime.date.today())
#     end_date = models.DateField()

#     def __str__(self):
#         return self.activity_name


# class Assignee(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     activity = models.ForeignKey(Activity, on_delete=models.PROTECT)

#     def __str__(self):
#         return self.user