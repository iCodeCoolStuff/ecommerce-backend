from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from ..models import User, Product, CartItem

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe",
                                                email="johndoe@gmail.com", password="password")

    def test_user_has_cart_associated_with_it_on_user_creation(self):
        try:
            cart = self.user.cart
        except ObjectDoesNotExist:
            self.fail("User does not have a cart associated with it on creation")


class CartModelTest(TestCase):

    def setUp(self):
        self.user    = User.objects.create_user(first_name="John", last_name="Doe",
                                                email="johndoe@gmail.com", password="password")

        self.cart    = self.user.cart
        self.product = Product.objects.create(name="Apple", price="0.99",
                                                description="A red apple")

    def test_get_total(self):

        #Test that when there are no items in the cart, get_total returns 0.0
        self.assertEqual(self.cart.get_total(), 0.0)

        cartitem_1 = CartItem.objects.create(product=self.product, quantity=2)
        cartitem_2 = CartItem.objects.create(product=self.product, quantity=3)

        self.cart.items.add(cartitem_1)
        self.cart.items.add(cartitem_2)

        self.assertEqual(self.cart.get_total(), 4.95)