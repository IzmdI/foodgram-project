from django.contrib import admin

from .models import Recipe, Ingredient, IngredientAmount, FoodTag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
    )
    search_fields = (
        "title",
        "author",
    )
    list_filter = (
        "title",
        "author",
        "tags",
    )
    inlines = (IngredientAmountInline,)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measure",
    )
    search_fields = ("name",)
    list_filter = ("name",)


class FoodTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FoodTag, FoodTagAdmin)
