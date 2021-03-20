from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_recipe, name="new_recipe"),
    path("favorites/", views.favorites, name="favorites"),
    path("follows/", views.follows, name="follows"),
    path("shoplist/", views.shoplist, name="shoplist"),
    path(
        "downloadshoplist/", views.download_shoplist, name="download_shoplist"
    ),
    path("recipes/<int:recipe_id>/", views.recipe_detail, name="recipe"),
    path(
        "recipes/<int:recipe_id>/edit/", views.recipe_edit, name="recipe_edit"
    ),
    path(
        "recipes/<int:recipe_id>/delete/",
        views.recipe_delete,
        name="recipe_delete",
    ),
    path("<str:username>/", views.profile, name="profile"),
]
