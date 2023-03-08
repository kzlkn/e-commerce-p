from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PaymentForm
from .models import ShoppingCart
from Useradmin.models import get_extended_user_from_user


def show_shopping_cart(request):
    # Local variables for template context
    shopping_cart_is_empty = True
    shopping_cart_items = None
    total_price = Decimal(0.0)

    if request.method == 'POST':
        # if user wants to clear shopping cart
        if 'empty' in request.POST:
            extended_user = get_extended_user_from_user(request.user)
            ShoppingCart.objects.get(related_user=extended_user).delete()

            context = {
                'shopping_cart_is_empty': shopping_cart_is_empty,
                'shopping_cart_items': shopping_cart_items,
                'total_price': 0.0
            }
            return render(request, 'shopping-cart.html', context)
        # if user wants to pay
        elif 'pay' in request.POST:
            return redirect('shopping-cart-checkout')

        # --- ShoppingCartItem Actions ---
        # if user wants to remove item from shopping cart
        elif 'remove-from-cart' in request.POST:
            extended_user = get_extended_user_from_user(request.user)
            shopping_cart = ShoppingCart.objects.get(related_user=extended_user)
            # gets value that was assigned to button in template (the productID)
            product_id = request.POST.get('remove-from-cart')
            shopping_cart.remove_item(product_id)
            return redirect('shopping-cart-show')

        # if user wants to increment quantity of item in shopping cart
        elif 'increment-quantity-of-item' in request.POST:
            extended_user = get_extended_user_from_user(request.user)
            product_id = request.POST.get('increment-quantity-of-item')
            shopping_cart_items = ShoppingCart.get_items(extended_user)
            item = shopping_cart_items.filter(product_id=product_id).get()
            item.increment_quantity()
            return redirect('shopping-cart-show')

        # if user wants to decrement quantity of item in shopping cart
        elif 'decrement-quantity-of-item' in request.POST:
            extended_user = get_extended_user_from_user(request.user)
            product_id = request.POST.get('decrement-quantity-of-item')
            shopping_cart_items = ShoppingCart.get_items(extended_user)
            item = shopping_cart_items.filter(product_id=product_id).get()
            item.decrement_quantity()
            return redirect('shopping-cart-show')

    else:
        if request.user.is_authenticated:
            extended_user = get_extended_user_from_user(request.user)
            shopping_cart = ShoppingCart.objects.filter(related_user=extended_user).first()
            if shopping_cart:
                shopping_cart_is_empty = False
                shopping_cart_items = ShoppingCart.get_items(extended_user=extended_user)
                total_price = shopping_cart.get_total_price()

        context = {
            'shopping_cart_is_empty': shopping_cart_is_empty,
            'shopping_cart_items': shopping_cart_items,
            'total_price': total_price
        }
        return render(request, 'shopping-cart.html', context)


@login_required(login_url='/useradmin/login')
def pay(request):
    shopping_cart_is_empty = True
    paid = False
    form = None
    extended_user = get_extended_user_from_user(request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        form.instance.extended_user = extended_user
        if form.is_valid():
            form.save()
            paid = True
            ShoppingCart.objects.get(related_user=extended_user).delete()  # empty shopping cart
        else:
            print(form.errors)
    else:
        shopping_cart = ShoppingCart.objects.filter(related_user=extended_user).first()
        if shopping_cart:
            shopping_cart_is_empty = False
            form = PaymentForm(initial={'amount': shopping_cart.get_total_price()})

    context = {
        'shopping_cart_is_empty': shopping_cart_is_empty,
        'payment_form': form,
        'paid': paid
    }
    return render(request, 'shopping-cart-checkout.html', context)
