from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User, Recipe, Ingredient, Follow
from .forms import RecipeForm


def index(request):
    recipes_list = Recipe.objects.all()
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "index.html", {"page": page, "paginator": paginator}
    )


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    profile_recipes = profile.recipes.all()
    paginator = Paginator(profile_recipes, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
        "profile": profile,
    }
    return render(request, "profile.html", context)


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_recipe_from_user = form.save(commit=False)
        new_recipe_from_user.author = request.user
        new_recipe_from_user.save()
        return redirect("index")

    return render(request, "new_recipe.html", {"form": form})
