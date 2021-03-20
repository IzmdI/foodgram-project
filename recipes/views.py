from django.http import FileResponse
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib.auth.decorators import login_required

from .models import Recipe, User, IngredientAmount
from .forms import RecipeForm, TagForm
from .utils import (
    get_paginator,
    is_follow,
    get_recipe_tags,
    get_recipe_ingredients,
    get_data,
)


OBJ_PER_PAGE = 6


def index(request):
    tags = request.GET.getlist("tags")
    form = TagForm(request.GET)
    if tags:
        recipes = Recipe.objects.filter(tags__slug__in=tags).distinct()
    else:
        recipes = Recipe.objects.all()
    page, paginator = get_paginator(request, recipes, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator, "form": form}
    return render(request, "index.html", context)


@login_required(login_url="/auth/login/")
def favorites(request):
    tags = request.GET.getlist("tags")
    form = TagForm(request.GET)
    if tags:
        recipes = (
            Recipe.objects.filter(favs__user=request.user)
            .filter(tags__slug__in=tags)
            .distinct()
        )
    else:
        recipes = Recipe.objects.filter(favs__user=request.user)
    page, paginator = get_paginator(request, recipes, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator, "form": form}
    return render(request, "favorites.html", context)


@login_required(login_url="/auth/login/")
def follows(request):
    authors = User.objects.filter(following__user=request.user)
    page, paginator = get_paginator(request, authors, OBJ_PER_PAGE)
    context = {"page": page, "paginator": paginator}
    return render(request, "follows.html", context)


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
    return render(request, "profile.html", context)


@login_required(login_url="/auth/login/")
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
    return render(request, "new_recipe.html", context)


@login_required(login_url="/auth/login/")
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect("recipe", recipe_id=recipe_id)

    form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    tags, ingredients, ing_amounts = get_data(request)
    if form.is_valid():
        recipe = form.save()
        get_recipe_tags(recipe, tags)
        get_recipe_ingredients(recipe, ingredients, ing_amounts)
        return redirect("recipe", recipe_id=recipe_id)

    context = {"form": form, "recipe": recipe}
    return render(request, "new_recipe.html", context)


@login_required(login_url="/auth/login/")
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
    return render(request, "recipe.html", context)


@login_required(login_url="/auth/login/")
def shoplist(request):
    recipes = Recipe.objects.filter(shoplists__user=request.user)
    context = {"recipes": recipes}
    return render(request, "shoplist.html", context)


@login_required(login_url="/auth/login/")
def download_shoplist(request):
    recipes = Recipe.objects.filter(shoplists__user=request.user)
    if not recipes:
        return redirect("index")
    ingredients = {}
    for recipe in recipes:
        items = IngredientAmount.objects.filter(recipe=recipe)
        for item in items:
            if ingredients.get(item.ingredient.name) is not None:
                ingredients[item.ingredient.name][0] += item.amount
            else:
                ingredients[item.ingredient.name] = [
                    item.amount,
                    item.ingredient.measure,
                ]
    file = open("static/shoplist.txt", "w+", encoding="UTF-8")
    for ingredient in ingredients:
        amount, measure = ingredients[ingredient]
        file.write(f" • {ingredient} ({measure}) - {amount}\n")
    file.close()
    file = open("static/shoplist.txt", "rb")
    return FileResponse(
        file, as_attachment=True, filename="Список_покупок.txt"
    )


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
