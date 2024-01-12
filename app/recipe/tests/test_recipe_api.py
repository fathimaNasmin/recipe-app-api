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


def create_user(**params):
    """Create and returns user."""
    return get_user_model().objects.create_user(**params)



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
        self.user = create_user(email='test@example.com', password='passwoerd12445')
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
        other_user = create_user(
            email='otheruser@example.com',
            password='otherusrpassword'
        )        
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user).order_by('-id')
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
        
    def test_partial_update(self):
        """Test the partial update of recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        
    def test_full_update(self):
        """Test the full update of recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
            price=Decimal('3.33'),
        )

        payload = {
            'title': 'New recipe title',
            'time_minutes': 5,
            'price': Decimal('5.30'),
            'link': 'https://www.example.com/recipe.pdf',
            'description': 'Sample recipe description'
            }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(self.user, recipe.user)
        
    def test_update_user_on_recipe_return_error(self):
        """Test returns error on update/change of user of a recipe."""
        new_user = create_user(email='testuser@example.com', password='password!223')
        recipe = create_recipe(user=self.user)
        
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user, recipe.user)
        
    def test_delete_recipe(self):
        """Test deleting the recipe."""
        recipe = create_recipe(user=self.user)
        
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        
    def test_delete_other_user_recipe_returns_error(self):
        """Test delete of other user recipe returns error."""
        other_user = create_user(email='newuser@example.com', password='newpassword')
        recipe = create_recipe(user=other_user)
        
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
