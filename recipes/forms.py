from django import forms

from .models import FoodTag, Ingredient, Recipe


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
        for ingredient, amount in zip(ingredients, ing_amounts):
            if not Ingredient.objects.filter(name=ingredient).exists():
                self.errors["ingredients"] = self.error_class(
                    ["Такого ингредиента нет в базе"]
                )
            if int(amount) < 0:
                self.errors["ingredients"] = self.error_class(
                    ["Количество не может быть отрицательным"]
                )
        return self.cleaned_data
