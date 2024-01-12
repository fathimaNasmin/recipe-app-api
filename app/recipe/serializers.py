"""
Serializers for Recipe api.
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer class for recipe."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']
        
        
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail."""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        
        
class TagSerializer(serializers.ModelSerializer):
    """Serializer class for tag."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
