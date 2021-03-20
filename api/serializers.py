from rest_framework import serializers

from recipes.models import Favorite, Follow, ShopList, Ingredient


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()
        model = Favorite


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()
        model = Follow


class ShopListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()
        model = ShopList


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()
        model = Ingredient
