from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from foodgram.settings import OBJ_PER_PAGE

from .forms import RecipeForm, TagForm
from .models import Ingredient, Recipe, User
from .utils import (
    get_data,
    get_paginator,
    get_recipe_ingredients,
    get_recipe_tags,
    is_follow,
)


def index(request):
    tags = request.GET.getlist("tags")
    form = TagForm(request.GET)
    if tags:
        recipes = Recipe.objects.filter(tags__slug__in=tags).distinct()
    else:
        recipes = Recipe.objects.all()
    page, paginator = get_paginator(request, recipes, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator, "form": form}
    return render(request, "recipes/index.html", context)


@login_required(login_url=reverse_lazy("login"))
def favorites(request):
    tags = request.GET.getlist("tags")
    form = TagForm(request.GET)
    if tags:
        recipes = request.user.fav_recipes.filter(
            tags__slug__in=tags
        ).distinct()
    else:
        recipes = request.user.fav_recipes.all()
    page, paginator = get_paginator(request, recipes, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator, "form": form}
    return render(request, "recipes/favorites.html", context)


@login_required(login_url=reverse_lazy("login"))
def follows(request):
    authors = User.objects.filter(following__user=request.user)
    page, paginator = get_paginator(request, authors, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator}
    return render(request, "recipes/follows.html", context)


def profile(request, username):
    tags = request.GET.getlist("tags")
    form = TagForm(request.GET)
    user = get_object_or_404(User, username=username)
    if tags:
        user_recipes = user.user_recipes.filter(tags__slug__in=tags).distinct()
    else:
        user_recipes = user.user_recipes.all()
    page, paginator = get_paginator(request, user_recipes, OBJ_PER_PAGE)
    context = {
        "page": page,
        "paginator": paginator,
        "profile": user,
        "is_follow": is_follow(request.user, user),
        "form": form,
    }
    return render(request, "recipes/profile.html", context)


@login_required(login_url=reverse_lazy("login"))
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    tags, ingredients, ing_amounts = get_data(request)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        get_recipe_tags(recipe, tags)
        get_recipe_ingredients(recipe, ingredients, ing_amounts)
        return redirect("index")

    context = {"form": form}
    return render(request, "recipes/new_recipe.html", context)


@login_required(login_url=reverse_lazy("login"))
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe_author = recipe.author
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect("recipe", recipe_id=recipe_id)

    form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    tags, ingredients, ing_amounts = get_data(request)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = recipe_author
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.save()
        get_recipe_tags(recipe, tags)
        get_recipe_ingredients(recipe, ingredients, ing_amounts)
        return redirect("recipe", recipe_id=recipe_id)

    context = {"form": form, "recipe": recipe}
    return render(request, "recipes/new_recipe.html", context)


@login_required(login_url=reverse_lazy("login"))
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect("recipe", recipe_id=recipe_id)

    recipe.delete()
    return redirect("profile", username=recipe.author.username)


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    context = {
        "recipe": recipe,
        "is_follow": is_follow(request.user, recipe.author),
    }
    return render(request, "recipes/recipe.html", context)


@login_required(login_url=reverse_lazy("login"))
def shoplist(request):
    recipes = request.user.purch_recipes.all()
    context = {"recipes": recipes}
    return render(request, "recipes/shoplist.html", context)


@login_required(login_url=reverse_lazy("login"))
def download_shoplist(request):
    recipes = request.user.purch_recipes.all()
    if not recipes:
        return redirect("index")
    ingredients = Ingredient.objects.filter(
        ing_amounts__recipe__in=recipes
    ).annotate(value=Sum("ing_amounts__amount"))
    with open("static/shoplist.txt", "w+", encoding="UTF-8") as file:
        for ingredient in ingredients:
            file.write(
                f" • {ingredient.name} ({ingredient.measure}) - {ingredient.value}\r\n"
            )
    return FileResponse(
        open("static/shoplist.txt", "rb"),
        as_attachment=True,
        filename="Список_покупок.txt",
    )


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
