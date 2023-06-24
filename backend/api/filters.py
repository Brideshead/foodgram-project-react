from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipesFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)
        else:
            return queryset.exclude(favorite_recipe__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        else:
            return queryset.exclude(shopping_cart__user=self.request.user)
