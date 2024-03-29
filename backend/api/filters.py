from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientsFilter(filters.FilterSet):
    """
    Фильтрация ингредиентов.

    Ищем по началу названия ингредиента.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(filters.FilterSet):
    """"
    Фильтрация вывода рецептов.

    На страницах рецептов, избранное,
    список покупок настроена фильтрация по тегам.

    def filter_is_favorited:
        Фильтрация по статусу аноним/пользователь на
        странице избранного.
    def filter_is_in_shopping_cart:
        Фильтрация по статусу аноним/пользователь на
        странице списка покупок.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(
                favorite_recipe__user=self.request.user,
            )
        return queryset.exclude(
            favorite_recipe__user=self.request.user,
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(
                shopping_cart__user=self.request.user,
            )
        return queryset.exclude(
            shopping_cart__user=self.request.user,
        )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags',
        )
