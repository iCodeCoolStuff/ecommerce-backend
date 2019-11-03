from django.test import TestCase
from django.test import SimpleTestCase

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import User, Product
from ..views  import UserListCreateView, UserRUDView

FACTORY = APIRequestFactory()

class APIStatusCodeTests(TestCase):

    def setUp(self):
        self.user = User(first_name="John", last_name="doe", email="johndoe@example.com")
        self.user.save()

        self.product = Product(name="Apple", price="1.00", description="A red apple.")
        self.product.save()

    def test_users_status_code(self):
        response = self.client.get('/api/v1/users/')
        self.assertEquals(response.status_code, 200)

    def test_user_detail_status_code(self):
        response = self.client.get(f'/api/v1/users/{self.user.pk}/')
        self.assertEquals(response.status_code, 200)

    def test_products_status_code(self):
        response = self.client.get('/api/v1/products/')
        self.assertEquals(response.status_code, 200)

    def test_product_detail_status_code(self):
        response = self.client.get('/api/v1/products/1/')
        self.assertEquals(response.status_code, 200)

class UserEndpointAPITest(TestCase):

    def setUp(self):
        self.user = User(first_name="Example", last_name="User", email="exampleuser@gmail.com", password="password")
        self.user.set_password('password')
        self.user.save()

    def test_create_user(self):
        request = FACTORY.post('/api/v1/users/', {
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
        request = FACTORY.post('/api/v1/users/', {
            'first_name': 'John',
            'last_name' : 'Doe',
            'email'     : 'johndoe@example.com',
            'password'  : 'password'}, format='json')
        view = UserListCreateView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
    
    def test_create_user_with_password_and_confirmation_mismatch(self):
        request = FACTORY.post('/api/v1/users/', {
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
        request = FACTORY.put(f'/api/v1/users/{self.user.pk}/', {
            'first_name': 'changed',
            'last_name' : 'changed',
            'email'     : 'changed@example.com',
            'password'  : 'password'}, format='json')
        view = UserRUDView.as_view()
        response = view(request, pk=self.user.pk)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_update_user_without_correct_password(self):
        request = FACTORY.put(f'/api/v1/users/{self.user.pk}/', {
            'first_name': 'changed',
            'last_name' : 'changed',
            'email'     : 'changed@example.com',
            'password'  : 'wordpass'}, format='json')
        view = UserRUDView.as_view()
        response = view(request, pk=self.user.pk)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Passwords do not match.")

class TokenAPITest(TestCase):

    def setUp(self):
        self.user = User(first_name="John", last_name="Doe", email="johndoe@gmail.com")
        self.user.set_password('password')
        self.user.save()

    def test_get_token_from_api(self):
        request = FACTORY.post('/api/v1/token/', {
            'email': 'johndoe@gmail.com',
            'password': 'password'
        }, format="json")
        view = TokenObtainPairView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
