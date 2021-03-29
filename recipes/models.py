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

    def by_tags(self, tags):
        if not tags:
            return self
        return self.filter(tags__slug__in=tags).distinct()


class FoodTag(models.Model):
    title = models.CharField(max_length=20, unique=True, verbose_name="Тэг")
    slug = models.SlugField(unique=True, verbose_name="Служ. имя")
    color = models.CharField(max_length=20, unique=True, verbose_name="Цвет")

    class Meta:
        verbose_name_plural = "Теги"
        verbose_name = "Тег"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title}"


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name="Ингредиент")
    measure = models.CharField(max_length=20, verbose_name="Ед. изм.")

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.measure}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_recipes",
        verbose_name="Автор",
    )
    title = models.CharField(max_length=30, verbose_name="Название")
    image = models.ImageField(
        upload_to="recipes/", blank=True, null=True, verbose_name="Изображение"
    )
    description = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        related_name="ing_recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        FoodTag,
        blank=True,
        related_name="tag_recipes",
        verbose_name="Тэги",
    )
    time = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(
                0, "Время приготовления не может быть отрицательным"
            ),
            MaxValueValidator(
                43260, "Вы собрались готовить это дольше месяца?"
            ),
        ],
        verbose_name="Время приготовления",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ["-pub_date", "title"]
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"

    def __str__(self):
        return f"{self.title}"

    def favorite_adds(self):
        return self.favs.count()

    favorite_adds.short_description = "В избранном"


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0, "Количество не может быть отрицательным"),
            MaxValueValidator(10000, "А куда вам столько?"),
        ],
        verbose_name="Количество",
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
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favs",
        verbose_name="Рецепт",
    )
    added = models.DateTimeField(
        verbose_name="Дата и время добавления",
        auto_now_add=True,
    )

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
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        help_text="Автор",
        verbose_name="Автор",
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
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoplists",
        verbose_name="Рецепт",
    )
    added = models.DateTimeField(
        verbose_name="Дата и время добавления",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-added"]
        verbose_name_plural = "Список покупок"
        verbose_name = "Список покупок"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("recipe")),
                name="Обнаружено дублирование",
            ),
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="shoplist_unique",
            ),
        ]

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в список покупок"
