from django.urls import path
from .views import *

app_name = "pos"

urlpatterns = [
    path('', pos, name='pos'),
]

