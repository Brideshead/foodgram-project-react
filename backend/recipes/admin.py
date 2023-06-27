from django.contrib import admin
from django.utils.html import format_html

from recipes.models import (FavoriteRecipes, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingCart, Subscribe, Tag)


class IngredientsInRecipeAdmin(admin.StackedInline):
    model = IngredientsInRecipe
    autocomplete_fields = ('ingredient',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    search_fields = (
        'name',
        'slug',
    )
    save_on_top = True
    empty_value_display = '-пусто'

    @admin.display(description='Цвет тега')
    def color_code(self, obj):
        return format_html(
            '<span style="color: #{};">{}</span>',
            obj.color[1:],
            obj.color,
        )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'get_favorites',
        'pub_date',
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name',
    )
    list_filter = (
        'name',
        'author__username',
        'tags__name',
    )
    inlines = (IngredientsInRecipeAdmin,)
    empty_value_display = '-пусто'

    @admin.display(description='Число добавлений в избранное')
    def get_favorites(self, data):
        return data.favorite_recipe.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    save_on_top = True
    empty_value_display = '-пусто'


@admin.register(FavoriteRecipes)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user',)
    empty_value_display = '-пусто'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user',)
    empty_value_display = '-пусто'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'subscriber',
    )
    list_filter = ('user',)
    search_fields = (
        'user__email',
        'subscriber__email',
    )
    empty_value_display = '-пусто'
