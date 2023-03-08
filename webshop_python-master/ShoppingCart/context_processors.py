from ShoppingCart.models import ShoppingCart
from Useradmin.models import get_extended_user_from_user


# Renders the number of items in the shopping cart of the user
# or 0 if no related shopping cart exists
# defined as context processor and registered under TEMPLATES in settings.py
# so any view can access this information
def shopping_cart_items_processor(request):
    shopping_cart_item_count = 0
    if request.user.is_authenticated:
        extended_user = get_extended_user_from_user(request.user)
        shopping_cart = ShoppingCart.objects.filter(related_user=extended_user).first()
        if shopping_cart:
            shopping_cart_item_count = shopping_cart.get_number_of_items()
    return {'shopping_cart_item_count': shopping_cart_item_count}
