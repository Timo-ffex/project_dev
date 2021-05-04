from django.urls import path
from .views import *

urlpatterns = [
    path('crop/', ListCrop.as_view()),
    path('crop/<int:pk>/', DetailCrop.as_view()),
    path('crop/season/', ListCropSeason.as_view()),
    path('crop/season/<int:pk>', DetailCropSeason.as_view()),
    path('crop/rotation/', ListCropRotation.as_view()),
    path('crop/rotation/<int:pk>', DetailCropRotation.as_view()),
    # path('points/', points, name='points'),
]