from django.http.response import JsonResponse
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Favorite, Follow, Ingredient, Recipe, ShopList, User

from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, ShopListSerializer)


class AddRemoveMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    model = None
    model_lookup_field = None

    def perform_create(self, serializer):
        if self.model_lookup_field == "recipe":
            recipe = get_object_or_404(Recipe, pk=self.request.data["id"])
            serializer.save(user=self.request.user, recipe=recipe)
        elif self.model_lookup_field == "author":
            author = get_object_or_404(User, pk=self.request.data["id"])
            serializer.save(user=self.request.user, author=author)

    def get_object(self):
        obj = None
        if self.model_lookup_field == "recipe":
            obj = get_object_or_404(
                self.model,
                recipe__pk=self.kwargs["pk"],
                user=self.request.user,
            )
        elif self.model_lookup_field == "author":
            obj = get_object_or_404(
                Follow, author__id=self.kwargs["pk"], user=self.request.user
            )
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return JsonResponse({"success": True}, status=status.HTTP_200_OK)


class FavoriteViewSet(AddRemoveMixin):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite
    model_lookup_field = "recipe"


class FollowViewSet(AddRemoveMixin):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    model = Follow
    model_lookup_field = "author"


class ShopListViewSet(AddRemoveMixin):
    serializer_class = ShopListSerializer
    queryset = ShopList.objects.all()
    model = ShopList
    model_lookup_field = "recipe"


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
