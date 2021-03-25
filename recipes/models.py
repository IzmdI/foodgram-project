from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class RecipeQuerySet(models.QuerySet):
    def params_for_user(self, user):
        if user.is_anonymous:
            return self
        shoplist = ShopList.objects.filter(
            recipe=models.OuterRef("pk"), user=user
        )
        favorite = Favorite.objects.filter(
            recipe=models.OuterRef("pk"), user=user
        )
        follow = Follow.objects.filter(
            author=models.OuterRef("author"), user=user
        )
        return self.annotate(
            is_in_basket=models.Exists(shoplist),
            is_in_favorites=models.Exists(favorite),
            is_follow=models.Exists(follow),
        )

    def in_basket(self, user):
        if user.is_anonymous:
            return self
        shoplists = ShopList.objects.filter(
            recipe=models.OuterRef("pk"), user=user
        )
        return self.filter(models.Exists(shoplists)).annotate(
            is_in_basket=models.Exists(shoplists)
        )

    def in_favorites(self, user):
        if user.is_anonymous:
            return self
        favorites = Favorite.objects.filter(
            recipe=models.OuterRef("pk"), user=user
        )
        return self.filter(models.Exists(favorites)).annotate(
            is_in_favorites=models.Exists(favorites)
        )

    def by_tags(self, tags):
        return self.filter(tags__slug__in=tags).distinct()


class FoodTag(models.Model):
    title = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Теги"
        verbose_name = "Тег"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title}"


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measure = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        ordering = ["name"]

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
    time = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1440)],
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ["-pub_date", "title"]
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"

    def favorite_adds(self):
        return Favorite.objects.filter(recipe_id=self.id).count()

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
    amount = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000000)],
    )

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
        ordering = ["user", "author"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="Обнаружена самоподписка",
            ),
            models.UniqueConstraint(
                fields=["user", "author"],
                name="follow_unique",
            ),
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
