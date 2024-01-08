"""Views for API"""

from rest_framework import generics 

from .serializers import UserSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """API view class to create new user"""
    serializer_class = UserSerializer