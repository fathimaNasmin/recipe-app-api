"""
Urls for user app.
"""
from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='create'),
    path('token/', views.CreateTokenAPIView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
