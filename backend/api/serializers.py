from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from core.models import (Ingredient, Recipe, RecipeIngredient, Favorite, ShopCart, Subscription)
from core.constants import (MAX_RECIPES_LIMIT,
                            RECIPE_INGREDIENT_AMOUNT_MIN_VALUE,
                            RECIPE_INGREDIENT_AMOUNT_MAX_VALUE,
                            RECIPE_COOKING_TIME_MIN_VALUE,
                            RECIPE_COOKING_TIME_MAX_VALUE
                            )

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['user', 'author']

    def validate(self, data):
        """Проверка подписки."""
        user = self.context['request'].user
        author = data['author']

        # Проверка на попытку подписки на самого себя
        if user == author:
            raise serializers.ValidationError('Действие невозможно для самого себя')

        # Проверка, что пользователь уже подписан
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError('Вы уже подписаны')

        return data

    def create(self, validated_data):
        """Создание подписки."""

        return Subscription.objects.create(**validated_data)

    def to_representation(self, instance):
        """Переопределение to_representation для вывода данных."""
        return {
            'status': 'Подписка успешно добавлена',
            'author': instance.author.username,
            'user': instance.user.username
        }


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user
        recipe = self.context['recipe']

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({'status': 'Рецепт уже в избранном'})

        return data

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'author': instance.recipe.author.username
        }


class ShopCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCart
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, data):
        """Проверка на повторное добавление."""
        user = self.context['request'].user
        recipe = self.context['recipe']

        if ShopCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({'status': 'Рецепт уже в корзине'})

        return data

    def create(self, validated_data):
        """Создание записи в корзине."""
        validated_data['user'] = self.context['request'].user
        return ShopCart.objects.create(**validated_data)

    def to_representation(self, instance):
        """Возвращает данные о рецепте после добавления в корзину."""
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'author': instance.recipe.author.username
        }


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (request and
                request.user.is_authenticated and
                author.subscribers.filter(
                    user=request.user).exists()
                )


class SiteUserSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')

    def get_recipes(self, author):
        recipes_limit = self.context.get('request').GET.get(
            'recipes_limit', MAX_RECIPES_LIMIT
        )

        try:
            recipes_limit = int(recipes_limit)
        except ValueError:
            recipes_limit = MAX_RECIPES_LIMIT

        return RecipeSerializer(
            author.recipes.all()[:recipes_limit],
            many=True,
            context=self.context
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(
        min_value=RECIPE_INGREDIENT_AMOUNT_MIN_VALUE,
        max_value=RECIPE_INGREDIENT_AMOUNT_MAX_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                obj.favorites.filter(user=request.user).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated and
                obj.shopcarts.filter(user=request.user).exists()
                )


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент.")
        ingredient_ids = [ingredient
                          ['ingredient'].id for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                "Дублирование ингредиентов не допускается.")

        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                "Поле 'image' не может быть пустым.")
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self.create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance.recipe_ingredients.all().delete()
        self.create_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def create_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['ingredient'].id,
                amount=ingredient['amount']
            ) for ingredient in ingredients_data)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True)
    cooking_time = serializers.IntegerField(
        min_value=RECIPE_COOKING_TIME_MIN_VALUE,
        max_value=RECIPE_COOKING_TIME_MAX_VALUE, required=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def to_representation(self, instance):
        if self.context.get('view') and getattr(self.context['view'],
                                                'action',
                                                None) in ['create', 'update']:
            return RecipeWriteSerializer(instance, context=self.context).data
        return RecipeReadSerializer(instance, context=self.context).data
