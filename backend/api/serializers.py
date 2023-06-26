import django.contrib.auth.password_validation as validators
# from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipes, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingCart, Subscribe, Tag, User)
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Сериализация для созданного пользователя.

    def get_is_subscribed:
        Проверяем наличии подписки.
        Returns:
            Если нет - просто False.
            Если да - модель пользователя-подписчика.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]
        ordering = ('id',)

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, subscriber=data.id).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Для созданого нового пользователя.

    def validate_password:
            Валидация вводимого пароля.
        Returns:
            Пароль прошедший валидацию.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            "password": {
                'write_only': True,
                'required': True,
            },
        }

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class TagSerializer(serializers.ModelSerializer):
    """Общиий сериализатор тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Базовый сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientsAddSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов на вход при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class IngredientsReadSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов при чтении рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeReadSeriaizer(serializers.ModelSerializer):
    """Серилазатор на чтение созданных рецептов.

    def get_is_favorited:
        Проверка добавлен ли рецепт в избранное.
    def get_is_in_shopping_cart:
        Проверка добавлен ли рецепт в список покупок.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsReadSerializer(
        many=True,
        read_only=True,
        source='ingredients_recipe',
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, instance):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
            user=user,
            recipe_id=instance.id,
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe_id=instance.id,
        ).exists()


class RecipeAddSerializer(serializers.ModelSerializer):
    """Серилазатор для добавления новых рецептов.

    def get_is_favorited:
        Проверка добавлен ли рецепт в избранное.
    def get_is_in_shopping_cart:
        Проверка добавлен ли рецепт в список покупок.
            Если нет - просто False.
            Если да- модель рецепта из списка покупок.
    def validate:
        Валидация входящей информации, в частности
        проверка уникальности ингредиентов и проверка
        наличия тега.
    def validate_ingredients:
        Валидация ингредиентов на вход, не менее
        определенного количества.
    def create:
        Переопределение базового метода для
        создание рецепта.
    def update:
        Переопределение базового метода для
        редактировани рецепта.
    def to_represantation:
        Переопределение базового метода для
        чтения созданного рецепта.
    """

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientsAddSerializer(
        many=True,
        source='ingredients_recipe',
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
        ]
        read_only_fields = ('author',)

    def get_is_favorited(self, instance):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
            user=user,
            recipe_id=instance.id,
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe_id=instance.id,
        ).exists()

    def validate(self, data):
        ingredients = data['ingredients_recipe']
        ingredient_list = []
        for ingredient in ingredients:
            # ingredient = get_object_or_404(
            #     Ingredient,
            #     id=items['ingredient']['id'].id,
            # )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!',
                )
            ingredient_list.append(ingredient)
        if len(ingredient_list) == 0:
            raise serializers.ValidationError(
                'Минимально должен быть 1 ингредиент в рецепте!',
            )
        for ingredient in ingredient_list:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Недопустимо количество ингредиента меньше 1!',
                )
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!',
            )
        return data

    # def validate_ingredients(self, ingredients):
    #     if not ingredients:
    #         raise serializers.ValidationError(
    #             'Минимально должен быть 1 ингредиент в рецепте!',
    #         )
    #     for ingredient in ingredients:
    #         if int(ingredient.get('amount')) < 1:
    #             raise serializers.ValidationError(
    #                 'Недопустимо меньше 1 ингредиента!',
    #             )
    #     return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        # for ingredient in ingredients:
        #     IngredientsInRecipe.objects.create(
        #         recipe=recipe,
        #         ingredient_id=ingredient['ingredient']['id'].id,
        #         amount=ingredient.get('amount'),
        #     )
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients_recipe')
        # instance.image = validated_data.get('image', instance.image)
        # instance.name = validated_data.get('name', instance.name)
        # instance.text = validated_data.get('text', instance.text)
        # instance.cooking_time = validated_data.get(
        #     'cooking_time', instance.cooking_time
        # )
        self.add_ingredients(recipe, ingredients)
        recipe.tags.clear()
        recipe.tags.set(validated_data.pop('tags'))
        return super().update(
            recipe,
            validated_data,
        )

    def to_representation(self, instance):
        return RecipeReadSeriaizer(
            instance,
            context={
                'request': self.context.get('request'),
            },
        ).data

    def add_ingredients(self, recipe, ingredients):
        recipe.ingredients.clear()
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(
                IngredientsInRecipe(
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                    ingredient_id=ingredient['ingredient']['id'].id,
                ),
            )
        IngredientsInRecipe.objects.bulk_create(ingredients_list)


class SubscribeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор подписки."""
    class Meta:
        model = Subscribe
        fields = ('user', 'subscriber')


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализация рецептов для подписки."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализация подписчиков.

    def get_is_subscribed:
        Проверка подписан или нет.
    def get_recipes:
        Получение рецептов.
    def get_recipes_count:
        Получение количества рецептов.
    """
    # email = serializers.ReadOnlyField(source='subscriber.email')
    # # id = serializers.ReadOnlyField(source='subscriber.id')
    # username = serializers.ReadOnlyField(source='subscriber.username')
    # first_name = serializers.ReadOnlyField(source='subscriber.first_name')
    # last_name = serializers.ReadOnlyField(source='subscriber.last_name')
    # is_subscribed = serializers.BooleanField(read_only=True)
    # recipes = serializers.SerializerMethodField()
    email = serializers.StringRelatedField()
    username = serializers.StringRelatedField()
    first_name = serializers.StringRelatedField()
    last_name = serializers.StringRelatedField()
    recipes = RecipeReadSeriaizer(
        read_only=True,
        many=True,
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',
        ordering = ('id',)

    # def get_is_subscribed(self, data):
    #     user = data.user
    #     if user.is_anonymous:
    #         return False
    #     return Subscribe.objects.filter(user=user,
    # subscriber=data.id).exists()

    # def get_recipes(self, instance):
    #     recipes = instance.subscriber.recipes.all()
    #     serializer = SubscribeRecipeSerializer(recipes, many=True)
    #     return serializer.data

    def get_recipes_count(self, instance):
        return instance.subscriber.recipes.all().count()


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Общий сериализатор для избранного и списка покупок."""
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipes
        fields = ('id', 'name', 'image', 'cooking_time')
