from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipesFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset.exclude(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(shoppinglist__user=self.request.user)
        return queryset.exclude(shoppinglist__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
    # tags = filters.CharFilter(
    #     field_name='tags__slug',
    #     method='filter_tags',
    # )
    # is_favorited = filters.CharFilter(
    #     field_name='is_favorited',
    #     method='filter_is_favorited',
    # )
    # is_in_shopping_cart = filters.CharFilter(
    #     field_name='is_in_shopping_cart',
    #     method='filter_is_in_shopping_cart',
    # )
    # author = filters.ModelChoiceFilter(queryset=User.objects.all())

    # class Meta:
    #     model = Recipe
    #     fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    # def filter_tags(self, queryset, name, tags):
    #     tags = self.request.query_params.getlist('tags')
    #     return queryset.filter(
    #         tags__slug__in=tags
    #     ).distinct()

    # def filter_is_favorited(self, queryset, name, value):
    #     if self.request.user.is_anonymous:
    #         return queryset
    #     if self.request.query_params.get(
    #         'is_favorited',
    #     ):
    #         return queryset.filter(
    #             favorite_recipe__user=self.request.user,
    #         ).distinct()
    #     return queryset

    # def filter_is_in_shopping_cart(self, queryset, name, value):
    #     if self.request.user.is_anonymous:
    #         return queryset
    #     if self.request.query_params.get(
    #         'is_in_shopping_cart',
    #     ):
    #         return queryset.filter(
    #             shopping_cart__user=self.request.user,
    #         ).distinct()
    #     return queryset
