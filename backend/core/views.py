from django.shortcuts import redirect
from .models import Recipe
from django.shortcuts import get_object_or_404


def short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(recipe.get_absolute_url())
