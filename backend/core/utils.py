from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def shopcart_or_favorite(self, request, model, serializer, pk):
    if request.method == 'POST':
        user = request.user
        recipe = self.get_object()
        if model.objects.filter(
            user=user,
            recipe=recipe,
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )
        added_recipe = model.objects.create(
            user=user,
            recipe=recipe,
        )
        output_serializer = serializer(added_recipe)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
    added_recipe = get_object_or_404(
        model,
        user=request.user,
        recipe__id=pk,
    )
    added_recipe.delete()
    return Response(
        status=status.HTTP_204_NO_CONTENT,
    )
