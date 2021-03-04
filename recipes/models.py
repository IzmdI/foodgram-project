from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measure = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Foodtag(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    tag = models.ManyToManyField(Foodtag, related_name="recipes")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientAmount", related_name="recipes"
    )
    time = models.CharField(max_length=10)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="amount"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="amount"
    )
    amount = models.IntegerField()


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
