from decimal import Decimal
from Useradmin.models import ExtendedUser
from django.db import models
from django.utils import timezone
from Article.models import get_related_article_from_article


# Create your models here.
class ShoppingCart(models.Model):
    related_user = models.ForeignKey(ExtendedUser,
                                     on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    # Get existing shopping cart or create a new one
    def add_item(extended_user, article):
        shopping_carts = ShoppingCart.objects.filter(related_user=extended_user)
        if shopping_carts:
            shopping_cart = shopping_carts.first()
        else:
            shopping_cart = ShoppingCart.objects.create(related_user=extended_user)

        # add article to cart
        product_id = article.id
        product_name = article.name
        product_manufacturer = article.manufacturer
        # get image related to shopping cart
        image = get_related_article_from_article(article).image
        # convert price to decimal
        price = convert_price_to_decimal(article.price)

        ShoppingCartItem.objects.create(product_id=product_id,
                                        product_name=product_name,
                                        product_manufacturer=product_manufacturer,
                                        price=price,
                                        image=image,
                                        shopping_cart=shopping_cart)

    def get_items(extended_user):
        shopping_cart = ShoppingCart.objects.filter(related_user=extended_user).first()
        return ShoppingCartItem.objects.filter(shopping_cart=shopping_cart)

    def get_number_of_items(self):
        return len(ShoppingCartItem.objects.filter(shopping_cart=self))

    def get_total_price(self):
        total_price = Decimal(0.0)  # set type to Decimal instead of float (to fit model)
        shopping_cart_items = ShoppingCartItem.objects.filter(shopping_cart=self)
        for item in shopping_cart_items:
            total_price += item.price * item.quantity
        return total_price

    def remove_item(self, product_id):
        ShoppingCartItem.objects.filter(product_id=product_id).delete()


class ShoppingCartItem(models.Model):
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    product_manufacturer = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(blank=True, null=True, default=None)
    shopping_cart = models.ForeignKey(ShoppingCart,
                                      on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product_name} | {self.price}€ | {self.quantity}'

    def increment_quantity(self):
        self.quantity = self.quantity + 1
        self.save()

    def decrement_quantity(self):
        if self.quantity > 1:
            self.quantity = self.quantity - 1
            self.save()
        if self.quantity == 1:
            self.shopping_cart.remove_item(self.product_id)


class Payment(models.Model):
    credit_card_number = models.CharField(max_length=19)  # Format: 1234 5678 9012 3456
    expiry_date = models.CharField(max_length=7)  # Format: 01/2000
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    timestamp = models.DateTimeField(default=timezone.now)
    extended_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)


def convert_price_to_decimal(price):
    # Replace comma to dot and get rid of € sign
    price = price.replace(',', '.').split("€")[0]
    return Decimal(price)
