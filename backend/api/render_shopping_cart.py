from django.utils.timezone import now


def render_shopping_cart(user, ingredients, recipes):
    shopping_cart_header = (
        f"Список покупок на {now().strftime('%d-%m-%Y %H:%M:%S')}\n"
    )

    ingredient_lines = [
        f"{idx}. {item['ingredient__name'].capitalize()} "
        f"({item['ingredient__measurement_unit']}) - {item['total_amount']}"
        for idx, item in enumerate(ingredients, start=1)
    ]

    recipe_lines = [
        f"- {recipe.name} (@{recipe.author.username})" for recipe in recipes
    ]

    return '\n'.join([
        shopping_cart_header,
        'Продукты:\n',
        *ingredient_lines,
        '\nРецепты, использующие эти продукты:\n',
        *recipe_lines
    ])
