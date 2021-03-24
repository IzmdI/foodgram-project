from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Follow, FoodTag, Ingredient, IngredientAmount


def get_paginator(request, queryset, value=10):
    paginator = Paginator(queryset, value)
    page_number = request.GET.get("page")
    if page_number is not None:
        if paginator.num_pages < page_number:
            page_number = paginator.num_pages
    page = paginator.get_page(page_number)
    return page, paginator


def is_follow(user, author):
    if user.is_anonymous:
        is_follow = False
    else:
        is_follow = Follow.objects.filter(user=user, author=author).exists()
    return is_follow


def get_recipe_tags(recipe, tags):
    for tag in tags:
        recipe.tags.add(get_object_or_404(FoodTag, slug=tag))


def get_recipe_ingredients(recipe, ingredients, ing_amounts):
    for ingredient, amount in zip(ingredients, ing_amounts):
        IngredientAmount.objects.get_or_create(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient, name=ingredient),
            amount=amount,
        )


def get_data(request):
    data = request.POST
    tags = data.getlist("tags")
    ingredients = {
        data.get(key): None for key in data if key.startswith("nameIngredient")
    }
    ing_amounts = [
        data.get(key) for key in data if key.startswith("valueIngredient")
    ]
    return tags, ingredients, ing_amounts
