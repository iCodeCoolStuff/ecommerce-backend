from django.test import TestCase
from django.test import SimpleTestCase

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import User, Product, CartItem
from ..views  import UserListCreateView, UserRUDView, CartItemViewSet

FACTORY = APIRequestFactory()

class APIStatusCodeTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe", 
                                                email="johndoe@gmail.com", password="password")

        self.product = Product(name="Apple", price="1.00", description="A red apple.")
        self.product.save()

    def test_users_status_code(self):
        response = self.client.get('/v1/users/')
        self.assertEquals(response.status_code, 200)

    def test_user_detail_status_code(self):
        response = self.client.get(f'/v1/users/{self.user.pk}/')
        self.assertEquals(response.status_code, 200)

    def test_user_detail_cart_status_code(self):
        response = self.client.get(f'/v1/users/{self.user.pk}/cart/')
        self.assertEquals(response.status_code, 200)

    def test_user_detail_cart_items_status_code(self):
        response = self.client.get(f'/v1/users/{self.user.pk}/cart/items/')
        self.assertEquals(response.status_code, 200)

    def test_user_detail_orders_status_code(self):
        response = self.client.get(f'/v1/users/{self.user.pk}/orders/')
        self.assertEquals(response.status_code, 200)

    def test_products_status_code(self):
        response = self.client.get('/v1/products/')
        self.assertEquals(response.status_code, 200)

    def test_product_detail_status_code(self):
        response = self.client.get(f'/v1/products/{self.product.slug}/')
        self.assertEquals(response.status_code, 200)

    def test_featured_products_status_code(self):
        response = self.client.get('/v1/products/featured/')
        self.assertEquals(response.status_code, 200)

    def test_new_products_status_code(self):
        response = self.client.get('/v1/products/new/')
        self.assertEquals(response.status_code, 200)
    
    def test_search_status_code(self):
        response = self.client.get('/v1/search?q=apple')
        self.assertEquals(response.status_code, 301)

    def test_recommendations_status_code(self):
        response = self.client.get(f'/v1/recommendations?id={self.product.id}')
        self.assertEquals(response.status_code, 200)


class UserEndpointAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe", 
                                                email="johndoe@gmail.com", password="password")

    def test_create_user(self):
        request = FACTORY.post('/v1/users/', {
            'first_name': 'John',
            'last_name' : 'Doe',
            'email'     : 'johndoe@example.com',
            'password'  : 'password',
            'password_confirmation': 'password'}, format='json')
        view = UserListCreateView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_create_user_without_password_confirmation(self):
        request = FACTORY.post('/v1/users/', {
            'first_name': 'John',
            'last_name' : 'Doe',
            'email'     : 'johndoe@example.com',
            'password'  : 'password'}, format='json')
        view = UserListCreateView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_with_password_and_confirmation_mismatch(self):
        request = FACTORY.post('/v1/users/', {
            'first_name': 'John',
            'last_name' : 'Doe',
            'email'     : 'johndoe@example.com',
            'password'  : 'password',
            'password_confirmation': 'wordpass'}, format='json')
        view = UserListCreateView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Password and confirmation do not match.")

    def test_update_user(self):
        request = FACTORY.put(f'/v1/users/{self.user.pk}/', {
            'first_name': 'changed',
            'last_name' : 'changed',
            'email'     : 'changed@example.com',
            'password'  : 'password'}, format='json')
        view = UserRUDView.as_view()
        response = view(request, pk=self.user.pk)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_update_user_without_correct_password(self):
        request = FACTORY.put(f'/v1/users/{self.user.pk}/', {
            'first_name': 'changed',
            'last_name' : 'changed',
            'email'     : 'changed@example.com',
            'password'  : 'wordpass'}, format='json')
        view = UserRUDView.as_view()
        response = view(request, pk=self.user.pk)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Passwords do not match.")


class CartEndpointAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe", 
                                                        email="johndoe@gmail.com", password="password")

        self.product = Product(name="Apple", price="1.00", description="A red apple.")
        self.product.save()

    def test_create_cartitem_in_user_shopping_cart(self):
        response = self.client.post(f'/v1/users/{self.user.pk}/cart/items/', {
            'product_id': self.product.pk,
            'quantity'  : 3}, format='json')
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_checkout_cart(self):
        cartitem = CartItem.objects.create(product=self.product, quantity=3)
        self.user.cart.items.add(cartitem)

        response = self.client.post(f'/v1/users/{self.user.pk}/cart/checkout', format="json")
        response.render()

        self.assertEqual(response.status_code, 201)

    def test_checkout_cart_with_no_items(self):
        response = self.client.post(f'/v1/users/{self.user.pk}/cart/checkout', format="json")
        response.render()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Cart cannot be empty.")


class TokenAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(first_name="John", last_name="Doe", 
                                                email="johndoe@gmail.com", password="password")

    def test_get_token_from_api(self):
        request = FACTORY.post('/v1/token/', {
            'email': 'johndoe@gmail.com',
            'password': 'password'
        }, format="json")
        view = TokenObtainPairView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


class RecommendationsAPITest(TestCase):
    
    def setUp(self):
        self.products = [
            Product(name="Apple", price="1.00", description="A red apple.", category=1),
            Product(name="Orange", price="1.00", description="An orange orange.", category=1),
            Product(name="Banana", price="1.00", description="A yellow banana.", category=1),
            Product(name="Peach", price="1.00", description="A pink peach.", category=1),
            Product(name="Mango", price="1.00", description="A vermillion mango.", category=1)
        ]

        for p in self.products:
            p.save()

    def test_recommendations(self):
        response = self.client.get(f'/v1/recommendations?id={self.products[0].pk}')
        self.assertEquals(response.status_code, 200)

    def test_recommendations_with_no_query_param(self):
        response = self.client.get(f'/v1/recommendations')
        self.assertEquals(response.status_code, 400)

    def test_recommendations_with_bad_query_param(self):
        response = self.client.get(f'/v1/recommendations?id=dfdf')
        self.assertEquals(response.status_code, 400)
    
    def test_recommendations_with_id_missing_in_database(self):
        response = self.client.get(f'/v1/recommendations?id=8374837873')
        self.assertEquals(response.status_code, 400)
    
    def test_recommendations_with_wrong_method(self):
        response = self.client.put(f'/v1/recommendations?id={self.products[0].pk}', {'name': 'basketball'})
        self.assertEquals(response.status_code, 405)