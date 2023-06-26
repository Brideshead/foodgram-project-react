from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import PageLimitPagination
from api.permissions import AdminAuthorOrReadOnly, AdminOrReadOnly
from api.serializers import (FavoriteShoppingCartSerializer,
                             IngredientSerializer, RecipeAddSerializer,
                             RecipeReadSeriaizer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer)
from core.utils import shopcart_or_favorite
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipes, Ingredient, Recipe, ShoppingCart,
                            Subscribe, Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class UsersViewSet(UserViewSet):
    """Вьюсет пользователей.

    def me:
        Кто вошёл.
    def subscribe:
        Подписаться или отписаться от автора.
        Подписаться на себя нельзя.
    def subscriptions:
        Получить на кого подписан пользователь.
    def perfom_create:
        Переопредления базового метода для
        создания пользователя и изменения пароля.
    """
    pagination_class = PageLimitPagination

    @action(
        detail=False,
        methods=['GET'],
        url_name='me',
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_name='subscribe',
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            user = request.user
            author = get_object_or_404(User, id=id)
            if user == author:
                return Response(
                    {'error': 'Вы не можете подписываться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscribe.objects.filter(user=user, subscriber=author).exists():
                return Response(
                    {'message': f'Вы уже подписаны на пользователя {author}!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscriber = Subscribe.objects.create(user=user, subscriber=author)
            serializer = SubscribeSerializer(
                subscriber,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, id=id)
            if user == author:
                return Response(
                    {'error': 'Вы не можете отписаться от самого себя!'},
                )
            subscriber = Subscribe.objects.filter(user=user, subscriber=author)
            if subscriber.exists():
                subscriber.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны!'},
                serializer.data,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_name='subscriptions',
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тэгов.

    Изменение и создание тэгов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filterset_class = IngredientsFilter
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """"Отображение рецептов.

    def get_serializer_class:
        В зависимости от запроса возвращает
        сериализатор создания или чтение рецепта.
    def favorite:
        Добавить или убрать рецепт из избранного.
    def shopping_cart:
        Добавление или удаление рецепта из
        спика покупок.
    def download_shopping_cart:
        Скачать список игредиентов для рецептов
        добавленных в список покупок.
    """

    queryset = Recipe.objects.all()
    permission_classes = (AdminAuthorOrReadOnly,)
    pagination_class = PageLimitPagination
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeAddSerializer
        return RecipeReadSeriaizer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_name='favorite',
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return shopcart_or_favorite(
            self,
            request,
            FavoriteRecipes,
            FavoriteShoppingCartSerializer,
            pk,
        )
        # if request.method == 'POST':
        #     user = request.user
        #     recipe = self.get_object()
        #     if FavoriteRecipes.objects.filter(
        #         user=user,
        #         recipe=recipe,
        #     ).exists():
        #         return Response(
        #             {'errors': 'Вы уже добавили рецепт в избранное!'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     favorite = FavoriteRecipes.objects.create(user=user,
        # recipe=recipe)
        #     serializer = FavoriteShoppingCartSerializer(favorite)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # if request.method == 'DELETE':
        #     favorite = get_object_or_404(
        #         FavoriteRecipes, user=request.user, recipe__id=pk
        #     )
        #     favorite.delete()
        #     return Response(
        #         {'message': 'Вы удалили рецепт из избранного!'},
        #         status=status.HTTP_204_NO_CONTENT,
        #     )
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_name='shopping_cart',
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return shopcart_or_favorite(
            self,
            request,
            ShoppingCart,
            FavoriteShoppingCartSerializer,
            pk,
        )
        # if request.method == 'POST':
        #     user = request.user
        #     recipe = self.get_object()
        #     if ShoppingCart.objects.filter(
        #         user=user,
        #         recipe=recipe,
        #     ).exists():
        #         return Response(
        #             {'errors': 'Вы уже добавили рецепт в корзину!'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     shopping_recipe = ShoppingCart.objects.create(
        #         user=user,
        #         recipe=recipe,
        #     )
        #     serializer = FavoriteShoppingCartSerializer(shopping_recipe)
        #     return Response(
        #         serializer.data,
        #         status=status.HTTP_201_CREATED,
        #     )
        # if request.method == 'DELETE':
        #     shopping_recipe = get_object_or_404(
        #         ShoppingCart,
        #         user=request.user,
        #         recipe_id=pk,
        #     )
        #     shopping_recipe.delete()
        #     return Response(
        #         {'message': 'Вы удалили рецепт из списка покупок!'},
        #         status=status.HTTP_204_NO_CONTENT,
        #     )
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        # buying_list = {}
        # user = request.user
        shopping_cart = (
            request.user.shopping_cart.recipes.
            values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        # ingredients = IngredientsInRecipe.objects.filter(
        #     recipe__shopping_cart__user=user,
        # )
        # for ingredient in ingredients:
        #     amount = ingredient.amount
        #     name = ingredient.ingredient.name
        #     measurement_unit = ingredient.ingredient.measurement_unit
        #     if name not in buying_list:
        #         buying_list[name] = {
        #             'amount': amount,
        #             'measurement_unit': measurement_unit,
        #         }
        #     else:
        #         buying_list[name]['amount'] = (
        #             buying_list[name]['amount'] + amount,
        #         )
        shopping_list = []
        for item, recipe in shopping_cart:
            shopping_list.append(
                f'{item} - {recipe["amount"]}, '
                f'{recipe["ingredients_measurement_unit"]}\n',
            )
        shopping_list_text = ''.join(shopping_list)
        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        response.write(shopping_list_text)
        return response
