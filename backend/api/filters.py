import django_filters
from core.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(
        field_name='author_id')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = django_filters.CharFilter(
        method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'is_in_shopping_cart', 'is_favorited']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов по наличию в корзине у текущего пользователя."""
        request = self.request
        if not request.user.is_authenticated:
            return queryset

        if value == '1':
            return queryset.filter(shopcarts__user=request.user)
        elif value == '0':
            return queryset.exclude(shopcarts__user=request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов по наличию в избранном у текущего пользователя."""
        request = self.request
        if not request.user.is_authenticated:
            return queryset

        if value == '1':
            return queryset.filter(favorites__user=request.user)
        elif value == '0':
            return queryset.exclude(favorites__user=request.user)
        return queryset
