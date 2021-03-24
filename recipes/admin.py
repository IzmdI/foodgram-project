from django.contrib import admin

from .models import FoodTag, Ingredient, IngredientAmount, Recipe


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "favorite_adds",
    )
    search_fields = (
        "title",
        "author",
    )
    list_filter = (
        "tags",
        "author",
    )
    inlines = (IngredientAmountInline,)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measure",
    )
    search_fields = ("name",)


class FoodTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "color")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FoodTag, FoodTagAdmin)
