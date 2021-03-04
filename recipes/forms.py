from django.forms import ModelForm

from .models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = (
            "name",
            "tag",
            "ingredients",
            "time",
            "description",
            "image",
        )
        labels = {
            "name": "Название рецепта",
            "tag": "Теги",
            "ingredients": "Ингредиенты",
            "time": "Время приготовления",
            "description": "Описание",
            "image": "Загрузить фото",
        }
