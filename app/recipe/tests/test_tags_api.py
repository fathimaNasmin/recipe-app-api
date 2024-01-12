"""Test tag api's."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status 

from core.models import Recipe, Tag

from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


def create_user(email='test@example.com', password='testpassword'):
    """Creates and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        
    def test_unauthenticated_user_access_fails(self):
        """Test unauthenticated user access fails."""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test authenticated user for accessing tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        
        res = self.client.get(TAG_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_tag_access_limited_to_user(self):
        """Test tag for only limited to the user who created."""
        new_user = create_user(email='newuser@example.com')
        Tag.objects.create(user=new_user, name='Vegan')
        
        tag = Tag.objects.create(user=self.user, name='Dessert')
        
        res = self.client.get(TAG_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
