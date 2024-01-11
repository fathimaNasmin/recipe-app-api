from decimal import Decimal

from django.urls import reverse 
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer 
)


RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """return url for recipe detail."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """create and returns recipe object."""
    default = {
        'title': 'Sample recipe title',
        'time_minutes': 5,
        'price': Decimal('5.30'),
        'link': 'https://www.example.com/recipe.pdf',
        'description': 'Sample recipe description'
    }
    default.update(params)
    
    recipe = Recipe.objects.create(user=user, **default)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated api requests."""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        """Test authentication required for api endpoint."""
        res = self.client.get(RECIPE_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'passwoerd12445'
        )
        self.client.force_authenticate(self.user)
        
    def test_recipe_retrieve_list(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPE_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_authenticated_user(self):
        """Test recipe list limited to the authenticated user."""
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'otherusrpassword'
        )        
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        
    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 5,
            'price': Decimal('5.30')
        }
        res = self.client.post(RECIPE_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)