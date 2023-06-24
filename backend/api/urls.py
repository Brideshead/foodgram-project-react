from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UsersViewSet)
from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UsersViewSet)
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(r'recipes', RecipeViewSet)


urlpatterns = [
     path('', include(router_v1.urls)),
     url(r'^auth/', include('djoser.urls')),
     url(r'^auth/', include('djoser.urls.authtoken')),
]
