from django.contrib import admin

from .models import Recipe, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    search_fields = (
        "name",
        "author",
    )
    list_filter = (
        "name",
        "author",
        "tag",
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measure",
    )
    search_fields = ("name",)
    list_filter = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
