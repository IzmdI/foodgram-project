from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class FoodTag(models.Model):
    title = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Теги"
        verbose_name = "Тег"

    def __str__(self):
        return f"{self.title}"


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measure = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"

    def __str__(self):
        return f"{self.name}, {self.measure}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_recipes"
    )
    title = models.CharField(max_length=30)
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        null=True,
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientAmount", related_name="ing_recipes"
    )
    tags = models.ManyToManyField(
        FoodTag, blank=True, related_name="tag_recipes"
    )
    time = models.PositiveIntegerField(blank=True, null=True)
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    favorites = models.ManyToManyField(
        User,
        through="Favorite",
        related_name="fav_recipes",
        blank=True,
    )
    purchases = models.ManyToManyField(
        User,
        through="ShopList",
        related_name="purch_recipes",
        blank=True,
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"

    def __str__(self):
        return f"{self.title}"


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
    )
    amount = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "amount", "recipe"],
                name="ingredient_unique",
            )
        ]

    def __str__(self):
        return f"{self.amount}"

    def __repr__(self):
        return f"{self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favs",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favs",
    )
    added = models.DateTimeField("Дата и время добавления", auto_now_add=True)

    class Meta:
        ordering = ["-added"]
        verbose_name_plural = "Избранные рецепты"
        verbose_name = "Избранный рецепт"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite_unique",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe} - {self.added}"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        help_text="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        help_text="Автор",
    )

    class Meta:
        verbose_name_plural = "Подписки"
        verbose_name = "Подписка"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="follow_unique"
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"


class ShopList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoplists",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoplists",
    )
    added = models.DateTimeField("Дата и время добавления", auto_now_add=True)

    class Meta:
        ordering = ["-added"]
        verbose_name_plural = "Список покупок"
        verbose_name = "Список покупок"

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в список покупок"
