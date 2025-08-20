from django.urls import path
from .views import *

urlpatterns = [
    path("register/", VerifyUserCodeView.as_view()),
]
