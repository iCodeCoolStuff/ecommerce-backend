from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from ..models import User

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe", 
                                                email="johndoe@gmail.com", password="password")

    def test_user_has_cart_associated_with_it_on_user_creation(self):
        try:
            cart = self.user.cart
        except ObjectDoesNotExist:
            self.fail("User does not have a cart associated with it on creation")