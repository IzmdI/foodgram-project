from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe, Favorite, Follow, User, ShopList, Ingredient

from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    ShopListSerializer,
    IngredientSerializer,
)


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.request.data["id"])
        serializer.save(user=self.request.user, recipe=recipe)

    def get_object(self):
        obj = get_object_or_404(
            Favorite, recipe__pk=self.kwargs["pk"], user=self.request.user
        )
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True})


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.request.data["id"])
        serializer.save(user=self.request.user, author=author)

    def get_object(self):
        obj = get_object_or_404(
            Follow, author__id=self.kwargs["pk"], user=self.request.user
        )
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True})


class ShopListViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ShopListSerializer
    queryset = ShopList.objects.all()

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.request.data["id"])
        serializer.save(user=self.request.user, recipe=recipe)

    def get_object(self):
        obj = get_object_or_404(
            ShopList, recipe__pk=self.kwargs["pk"], user=self.request.user
        )
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        query = self.request.query_params.get("query")
        if query is not None:
            queryset = queryset.filter(name__istartswith=query)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ingredients = []
        for item in queryset:
            ingredients.append({"title": item.name, "dimension": item.measure})
        return Response(ingredients)
