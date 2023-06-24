from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import PageLimitPagination
from api.permissions import AdminAuthorOrReadOnly, AdminOrReadOnly
from api.serializers import (FavoriteGetSerializer, IngredientSerializer,
                             RecipeAddSerializer, RecipeReadSeriaizer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipes, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingCart, Subscribe, Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class UsersViewSet(UserViewSet):

    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserSerializer

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
        """Получить на кого пользователь подписан."""

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
        if request.method == 'POST':
            user = request.user
            recipe = self.get_object()
            if FavoriteRecipes.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                return Response(
                    f'Вы уже добавили рецепт {recipe} в избранное!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = FavoriteRecipes.objects.create(user=user, recipe=recipe)
            serializer = FavoriteGetSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                FavoriteRecipes, user=request.user, recipe__id=pk
            )
            favorite.delete()
            return Response(
                f'Вы удалили рецепт {recipe} из избранного!',
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
            detail=True,
            methods=['POST', 'DELETE'],
            url_name='shopping_cart',
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': request.user.id, 'recipe': pk}
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = FavoriteGetSerializer(recipe)
            return Response(
                f'Вы добавили {recipe} в список покупок!',
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        ShoppingCart.objects.filter(
            user=serializer.data.get('user'),
            recipe=serializer.data.get('recipe')).delete()
        return Response(
            {'message': f'Вы удалили {recipe} из списка покупок!'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=['GET'],
        detail=False,
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        buying_list = {}
        user = request.user
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=user,
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit,
                }
            else:
                buying_list[name]['amount'] = (
                    buying_list[name]['amount'] + amount,
                )
        shopping_list = []
        for item in buying_list:
            shopping_list.append(
                f'{item} - {buying_list[item]["amount"]}, '
                f'{buying_list[item]["measurement_unit"]}\n'
            )
        shopping_list_text = ''.join(shopping_list)
        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        response.write(shopping_list_text)
        return response
