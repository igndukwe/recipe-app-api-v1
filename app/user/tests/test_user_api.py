from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# URL for creating users
# ../user/create/
CREATE_USER_URL = reverse('user:create')
# URL neeted to make the HTTP POST request
# ../user/me/
TOKEN_URL = reverse('user:token')
# ../user/me/
ME_URL = reverse('user:me')


# Helper Function to create a user for each test
# **params: you can add as much parameters
def create_user(**params):
    return get_user_model().objects.create_user(**params)

# Public API are unauthenticated API e.g create user


class PublicUserApiTest(TestCase):
    """Test the users API (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valied_user_success(self):
        """Test creating user with valied payload is successful
        """
        # requirments for creating user
        payload = {
            'email': 'test@gmail.com',
            'password': 'abcd1234',
            'name': 'Test name'
        }

        # this will do a HTTP POST request and create a user
        response = self.client.post(CREATE_USER_URL, payload)

        # Check if statuscode returns a HTTP201 exception when created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that the user is actually created
        # response.data is a dic responce like our payload
        # but with an additional id field
        user = get_user_model().objects.get(**response.data)
        # this will assert that the password is true
        self.assertTrue(user.check_password(payload['password']))
        # Ensure that password is not returned in the request
        # because it is a potential security voulnarability
        self.assertNotIn('password', response.data)

    # what if we create a user that already exists
    def test_user_exists(self):
        """Test creating user that already exists fails
        """
        # requirments for creating user
        payload = {
            'email': 'test@gmail.com',
            'password': 'abcd1234',
            'name': 'Test',
        }

        # call the create function above
        create_user(**payload)

        # this will do a HTTP POST request and create a user
        response = self.client.post(CREATE_USER_URL, payload)

        # Check if statuscode returns a HTTP400 bad request
        # becos user already exist
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # test if password is too shore
    def test_password_too_short(self):
        """Test that password must be more than 5 characters
        """
        # requirments for creating user
        payload = {
            'email': 'test@gmail.com',
            'password': 'pwd',
            'name': 'Test',
        }

        # this will do a HTTP POST request and create a user
        response = self.client.post(CREATE_USER_URL, payload)

        # Ensure that statuscode returns a HTTP400 bad request
        # becos must exist before we can ckeck password
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # chech if user exists true else false
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'abcd1234',
        }

        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        # We expect a token and should get a HTTP 200
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given
        """
        # create user
        create_user(email='test@gmail.com', password='abcd1234')
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrong'
        }
        # We do not expect a token and should get a HTTP 400
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doens't exist
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
        }
        # make a request without creating a user
        response = self.client.post(TOKEN_URL, payload)

        # We do not expect a token and should get a HTTP 400
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required
        """
        payload = {
            'email': 'one',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)

        # We do not expect a token and should get a HTTP 400
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication required for users"""
        # HTTP GET Request
        response = self.client.get(ME_URL)

        # If you call the URL without authorization
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Private API are authenticated API e.g update user, change password
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    # setup for authentication
    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='abcd1234',
            name='fname',
        )
        self.client = APIClient()
        # helper function that makes it easy to simulate authentication request
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
