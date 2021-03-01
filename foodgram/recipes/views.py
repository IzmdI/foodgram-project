from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Recipe, Ingredient, Follow


def index(request):
    recipes_list = Recipe.objects.all()
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "Index.html", {"page": page, "paginator": paginator}
    )
