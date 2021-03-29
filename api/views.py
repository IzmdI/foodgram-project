from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from rest_framework import mixins, status, viewsets
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
            try:
                recipe = Recipe.objects.get(pk=self.request.data["id"])
            except ObjectDoesNotExist:
                return JsonResponse(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(user=self.request.user, recipe=recipe)
        elif self.model_lookup_field == "author":
            try:
                author = User.objects.get(pk=self.request.data["id"])
            except ObjectDoesNotExist:
                return JsonResponse(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(user=self.request.user, author=author)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return JsonResponse({"success": True}, status=status.HTTP_201_CREATED)

    def get_object(self):
        obj = None
        if self.model_lookup_field == "recipe":
            try:
                obj = self.model.objects.get(
                    recipe__pk=self.kwargs["pk"], user=self.request.user
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif self.model_lookup_field == "author":
            try:
                obj = self.model.objects.get(
                    author__id=self.kwargs["pk"], user=self.request.user
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {"success": False},
                    status=status.HTTP_400_BAD_REQUEST,
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
