import django.contrib.auth.password_validation as validators
from django.shortcuts import get_object_or_404
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
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {"password": {
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
        fields = ['id', 'name', 'color', 'slug']


# class TaggedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tagged
#         fields = ['id', 'recipe', 'tag']


class IngredientSerializer(serializers.ModelSerializer):
    """Базовый сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов, входящих в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name',
    )
    measurement_unit = (
        serializers.CharField(
            read_only=True,
            source='ingredient.measurement_unit',
        ),
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientsAddSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов при создании рецепта."""

    # id = serializers.IntegerField()

    # class Meta:
    #     model = Ingredient
    #     fields = ['id', 'amount']
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )

    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = (
        serializers.CharField(
            read_only=True,
            source='ingredient.measurement_unit'))

    class Meta:
        model = IngredientsInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name',
    )
    measurement_unit = (
        serializers.CharField(
            read_only=True,
            source='ingredient.measurement_unit'),
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSeriaizer(serializers.ModelSerializer):
    """Серилазатор на чтение созданных рецептов.

    def get_is_favorited:
        Проверка добавлен ли рецепт в избранное.
        Returns:
            Если нет - просто False.
            Если да- модель избранного рецепта.
    def get_is_in_shopping_cart:
        Проверка добавлен ли рецепт в список покупок.
            Если нет - просто False.
            Если да- модель рецепта из списка покупок.
    def validate_ingredients:
        Валидация добавляемых ингредиентов.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsReadSerializer(
        many=True,
        read_only=True,
        source='recipes',
    )
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
    """Серилазатор на чтение созданных рецептов.

    def get_is_favorited:
        Проверка добавлен ли рецепт в избранное.
        Returns:
            Если нет - просто False.
            Если да- модель избранного рецепта.
    def get_is_in_shopping_cart:
        Проверка добавлен ли рецепт в список покупок.
            Если нет - просто False.
            Если да- модель рецепта из списка покупок.
        Returns:
            ValidationError если количество ингредиентов
            меньше одного, или если в рецепт вообще не
            добавлены ингредиенты, также проверяет что
            в рецепт входят только уникальные ингредиенты.
            Если ингредиенты проходят валидацию,
            возвращает список ингредиентов.
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
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['ingredient']['id'].id)
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!')
        return data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientsInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['ingredient']['id'].id,
                amount=ingredient.get('amount'),
            )
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredients:
                IngredientsInRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                )
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)
        # validated_data['author'] = self.context.get('request').user
        # tags = validated_data.pop('tags')
        # ingredients = validated_data.pop('ingredients_recipe')
        # Tagged.objects.filter(recipe=instance).delete()
        # IngredientsInRecipe.objects.filter(recipe=instance).delete()
        # self.add_tags(instance, tags)
        # self.add_ingredients(instance, ingredients)
        # return super().update(instance, validated_data)

    # def add_tags(self, instance, tags):
    #     for tag in tags:
    #         Tagged.objects.create(tag=tag, recipe=instance)

    # def add_ingredients(self, recipe, ingredients):
    #     for ingredient in ingredients:
    #         current_ingredient = (
    #             get_object_or_404(
    #                 Ingredient,
    #                 id=ingredient.get('id'),
    #             ),
    #         )
    #         IngredientsInRecipe.objects.create(
    #             ingredient=current_ingredient,
    #             amount=ingredient.get('amount'),
    #             recipe=recipe,
    #         )
    def to_representation(self, instance):
        return RecipeReadSeriaizer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
        # get_object_or_404(User, id=instance.author.id)
        # user = self.context.get('request').user
        # if user.is_anonymous:
        #     favorite = False
        #     shopping_cart = False
        # else:
        #     favorite = FavoriteRecipes.objects.filter(
        #         user=user,
        #         recipe=instance.id,
        #     ).exists()
        #     shopping_cart = ShoppingCart.objects.filter(
        #         user=user,
        #         recipe=instance.id,
        #     ).exists()
        # representation = super().to_representation(instance)
        # representation['is_favorited'] = favorite
        # representation['is_in_shopping_cart'] = shopping_cart
        # return representation


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['user', 'subscriber']


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='subscriber.email')
    id = serializers.ReadOnlyField(source='subscriber.id')
    username = serializers.ReadOnlyField(source='subscriber.username')
    first_name = serializers.ReadOnlyField(source='subscriber.first_name')
    last_name = serializers.ReadOnlyField(source='subscriber.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        read_only_fields = '__all__',
        ordering = ('id',)

    def get_is_subscribed(self, data):
        user = data.user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, subscriber=data.id).exists()

    def get_recipes(self, instance):
        recipes = instance.subscriber.recipes.all()
        serializer = SubscribeRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, instance):
        return instance.subscriber.recipes.all().count()


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipes
        fields = ['id', 'name', 'image', 'cooking_time']
