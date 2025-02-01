from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
]