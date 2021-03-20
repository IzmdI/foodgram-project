from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r"favorites", views.FavoriteViewSet, basename="favorites")
router.register(
    r"subscriptions", views.FollowViewSet, basename="subscriptions"
)
router.register(r"purchases", views.ShopListViewSet, basename="purchases")
router.register(
    r"ingredients", views.IngredientViewSet, basename="ingredients"
)

urlpatterns = [
    path("", include(router.urls)),
]
