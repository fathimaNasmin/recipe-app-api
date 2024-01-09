"""Views for API"""

from rest_framework import generics, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserAPIView(generics.CreateAPIView):
    """API view class to create new user"""
    serializer_class = UserSerializer
    
     
class CreateTokenAPIView(ObtainAuthToken):
    """API view class to create token for authenticated users."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
    
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manages the authenticated users."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user