from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from foodgram.settings import OBJ_PER_PAGE

from .forms import RecipeForm, TagForm
from .models import IngredientAmount, Recipe, User
from .utils import get_paginator, is_follow


def index(request):
    tags = request.GET.getlist("tags")
    tagsfull = True if not tags or len(tags) == 3 else False
    if len(tags) == 3:
        return redirect("index")

    form = TagForm(request.GET)
    recipes = Recipe.objects.by_tags(tags).params_for_user(request.user)
    page, paginator, page_num = get_paginator(request, recipes, OBJ_PER_PAGE)
    if page is None:
        return redirect(
            request.get_full_path().replace(
                "page=%s" % page_num, "page=%s" % paginator.num_pages
            )
        )

    context = {
        "page": page,
        "paginator": paginator,
        "form": form,
        "tagsfull": tagsfull,
    }
    return render(request, "recipes/index.html", context)


@login_required(login_url=reverse_lazy("login"))
def favorites(request):
    tags = request.GET.getlist("tags")
    tagsfull = True if not tags or len(tags) == 3 else False
    if len(tags) == 3:
        return redirect("favorites")

    form = TagForm(request.GET)
    recipes = (
        Recipe.objects.by_tags(tags)
        .params_for_user(request.user)
        .filter(is_in_favorites=True)
    )
    page, paginator, page_num = get_paginator(request, recipes, OBJ_PER_PAGE)
    if page is None:
        return redirect(
            request.get_full_path().replace(
                "page=%s" % page_num, "page=%s" % paginator.num_pages
            )
        )

    context = {
        "page": page,
        "paginator": paginator,
        "form": form,
        "tagsfull": tagsfull,
    }
    return render(request, "recipes/favorites.html", context)


@login_required(login_url=reverse_lazy("login"))
def follows(request):
    follows = request.user.follower.only("author")
    page, paginator, page_num = get_paginator(request, follows, OBJ_PER_PAGE)
    if page is None:
        return redirect(
            request.get_full_path().replace(
                "page=%s" % page_num, "page=%s" % paginator.num_pages
            )
        )

    context = {"page": page, "paginator": paginator}
    return render(request, "recipes/follows.html", context)


def profile(request, username):
    tags = request.GET.getlist("tags")
    tagsfull = True if not tags or len(tags) == 3 else False
    if len(tags) == 3:
        return redirect("profile", username)

    form = TagForm(request.GET)
    user = get_object_or_404(User, username=username)
    user_recipes = user.user_recipes.by_tags(tags).params_for_user(
        request.user
    )
    page, paginator, page_num = get_paginator(
        request, user_recipes, OBJ_PER_PAGE
    )
    if page is None:
        return redirect(
            request.get_full_path().replace(
                "page=%s" % page_num, "page=%s" % paginator.num_pages
            )
        )

    context = {
        "page": page,
        "paginator": paginator,
        "profile": user,
        "is_follow": is_follow(request.user, user),
        "form": form,
        "tagsfull": tagsfull,
    }
    return render(request, "recipes/profile.html", context)


@login_required(login_url=reverse_lazy("login"))
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save(request)
                return redirect("index")
        except IntegrityError:
            raise HttpResponseBadRequest

    context = {"form": form}
    return render(request, "recipes/new_recipe.html", context)


@login_required(login_url=reverse_lazy("login"))
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect("recipe", recipe_id=recipe_id)

    form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save(request)
                return redirect("recipe", recipe_id=recipe_id)
        except IntegrityError:
            raise HttpResponseBadRequest

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
    recipe = get_object_or_404(
        Recipe.objects.params_for_user(request.user),
        pk=recipe_id,
    )
    context = {"recipe": recipe}
    return render(request, "recipes/recipe.html", context)


@login_required(login_url=reverse_lazy("login"))
def shoplist(request):
    recipes = Recipe.objects.params_for_user(request.user).filter(
        is_in_basket=True
    )
    context = {"recipes": recipes}
    return render(request, "recipes/shoplist.html", context)


@login_required(login_url=reverse_lazy("login"))
def download_shoplist(request):
    recipes = Recipe.objects.params_for_user(request.user).filter(
        is_in_basket=True
    )
    if not recipes:
        return redirect("index")

    ingredients = (
        IngredientAmount.objects.filter(recipe__in=recipes)
        .values(name=F("ingredient__name"), measure=F("ingredient__measure"))
        .annotate(value=Sum("amount"))
    )
    content = ""
    for item in ingredients:
        content += f" • {item['name']} ({item['measure']}) - {item['value']}\r\n"

    content = bytes(content, encoding="UTF-8")
    uploaded_file = SimpleUploadedFile(
        name="Список_покупок.txt", content=content
    )
    return FileResponse(
        uploaded_file, as_attachment=True, filename="Список_покупок.txt"
    )


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
