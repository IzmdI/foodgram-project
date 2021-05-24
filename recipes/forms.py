from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.http import HttpResponseBadRequest

from .models import FoodTag, Ingredient, Recipe
from .utils import get_data, get_recipe_ingredients, get_recipe_tags


class TagForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=FoodTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        to_field_name="slug",
        required=False,
    )


class RecipeForm(forms.ModelForm, TagForm):
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

    def clean(self):
        super(RecipeForm, self).clean()
        if not self.cleaned_data["tags"]:
            self.errors["tags"] = self.error_class(
                ["Выберите хотя бы один тэг"]
            )
        ingredients = [
            self.data.get(key)
            for key in self.data
            if key.startswith("nameIngredient")
        ]
        ing_amounts = [
            self.data.get(key)
            for key in self.data
            if key.startswith("valueIngredient")
        ]
        if not ingredients:
            self.errors["ingredients"] = self.error_class(
                ["Добавьте хотя бы один ингредиент"]
            )
        for ingredient, amount in zip(ingredients, ing_amounts):
            if not Ingredient.objects.filter(name=ingredient).exists():
                self.errors["ingredients"] = self.error_class(
                    ["Ингредиента нет в базе"]
                )
            if int(amount) < 0 or int(amount) > 10000:
                self.errors["ingredients"] = self.error_class(
                    ["Количество не может быть отрицательным или больше 10000"]
                )
        return self.cleaned_data

    def save(self, request):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        tags, ingredients, ing_amounts = get_data(request)
        try:
            with transaction.atomic():
                try:
                    self.instance.author
                except ObjectDoesNotExist:
                    self.instance.author = request.user
                self.instance.save()
                get_recipe_tags(self.instance, tags)
                get_recipe_ingredients(self.instance, ingredients, ing_amounts)
        except IntegrityError:
            raise HttpResponseBadRequest
        return self.instance
