from django.core import validators
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=250,
        unique=True,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Номер цвета',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'Тег {self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=250,
        help_text='Укажите единицу измерения',
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'name',
                    'measurement_unit',
                ],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'Ингридиент {self.name} ед.измерения: {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=250,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='static/recipe/',
        null=False,
        verbose_name='Фото рецепта',
    )
    text = models.TextField(
        help_text='Текстовое описание рецепта',
    )
    # ingredients = models.ManyToManyField(
    #     Ingredient,
    #     through='IngredientsInRecipe',
    #     verbose_name='Ингредиенты',
    # )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
                validators.MinValueValidator(
                    1,
                    message='Минимальное время приготовления = 1 минута',
                ),
        ],
        verbose_name='Время приготовления',
    )
    is_favorited = models.ManyToManyField(
        User,
        through='FavoriteRecipes',
        related_name='is_favorited',
        verbose_name='В избранном',
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        through='ShoppingCart',
        related_name='in_shopping_cart',
        verbose_name='В списке покупок',
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Автор {self.author}, название рецепта: {self.name}.'


# class Tagged(models.Model):
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     'recipe',
#                     'tag',
#                 ],
#                 name='unique_tag_per_recipe',
#             )
#         ]
#         verbose_name = 'tag_per_recipe'
#         verbose_name_plural = 'tags_per_recipe'


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='В каких рецептах',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Связанные ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            validators.MinValueValidator(
                1,
                message='Минимальное количество ингридиентов = 1',
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient',
                ],
                name='unique_ingredient_per_recipe',
            ),
        ]
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self):
        return f'Ингридиент {self.ingredient} кол-во: {self.amount}'


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                        'recipe',
                        'user',
                ],
                name='unique_favorite_recipe',
            ),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Пользователь {self.user} добавил {self.recipe} в избранное.'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'user',
                ],
                name='unique_shopping_list_recipe',
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'Пользователь {self.user}'
                f'добавил ингредиенты {self.recipe} в покупки.')


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Пользователь',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'subscriber',
                ],
                name='unique_subscriber',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user} подписался на {self.subscriber}'
