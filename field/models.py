from django.db import models
from django.contrib.auth.models import Group, User
# from django.contrib.gis.db import models as g_models
import datetime


def year_choices():
    return [(r,r) for r in range(2000, datetime.date.today().year+1)]

def current_year():
    return datetime.date.today().year


class Field(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    group_name = models.CharField(max_length=100, null=True)
    farm_size = models.FloatField(default=0.0)
    field_coordinate = models.JSONField(default=dict)
    # draw_field = g_models.PolygonField()


    # starting_longitude = models.DecimalField(max_digits=9, decimal_places=6, unique=True)
    # starting_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    # ending_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    # ending_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=False)

    # class Meta:
    #     unique_together = ('starting_longitude', 'starting_latitude',)

    def __str__(self):
        return self.field_name


class Activity(models.Model):
    field = models.ForeignKey(Field, on_delete=models.PROTECT)
    activity_name = models.CharField(max_length=25, null=False, default='')
    activity_type = models.CharField(max_length=25, default='', null=False)
    description = models.TextField(default='')
    planned_cost = models.FloatField(default=0.0, null=False)
    actual_cost = models.FloatField(default=0.0, null=False)
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.name


class AssignFarmActivity(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    team_member_id = models.CharField(max_length=25)

