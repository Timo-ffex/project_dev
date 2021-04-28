from django.db import models
from field.models import Field
from django.contrib.auth.models import Group, User
import datetime


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