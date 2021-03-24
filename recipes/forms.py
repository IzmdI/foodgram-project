from django import forms

from .models import FoodTag, Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=FoodTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        to_field_name="slug",
        required=False,
    )
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.TextInput(attrs={"id": "nameIngredient"}),
        to_field_name="name",
    )

    class Meta:
        model = Recipe
        fields = (
            "title",
            "tags",
            "ingredients",
            "time",
            "description",
            "image",
        )
        labels = {
            "title": "Название рецепта",
            "tags": "Теги",
            "ingredients": "Ингредиенты",
            "time": "Время приготовления",
            "description": "Описание",
            "image": "Загрузить фото",
        }


class TagForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=FoodTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        to_field_name="slug",
        required=False,
    )
