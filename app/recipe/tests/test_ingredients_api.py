from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

# ../recipe/ingredient-list/
INGREDIENTS_URL = reverse('recipe:ingredient-list')

# Assuming you are a public user that want to access this URL
# test that login is required


class PublicIngredientsApiTests(TestCase):
    """Test the publically available ingredients API"""

    # add unauthenticated client
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access this endpoint"""

        # client try to access this url
        response = self.client.get(INGREDIENTS_URL)

        # access fails because client is not athenticated
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Test that authenticated users can access the Ingredient model


class PrivateIngredientsAPITests(TestCase):
    """Test ingredients can be retrieved by authorized user"""

    # setup authenticated client
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""

        # create two ingredients by user and save in DB
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='salt')

        # Client access HTTP GET Response to retrieve data from DB
        response = self.client.get(INGREDIENTS_URL)

        # list all ingredients from the DB
        # order by name in reverse order
        ingredients = Ingredient.objects.all().order_by('-name')
        # Serialize many ingredents from PYTHON NATIVE to JSON
        serializer = IngredientSerializer(ingredients, many=True)

        # check the statuscode and the data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )

        # create ingredient object with new user in DB
        Ingredient.objects.create(user=user2, name='Vinegar')

        # create ingredient object with initial authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name='tumeric')

        # Client access HTTP GET Response to retrieve data from DB
        response = self.client.get(INGREDIENTS_URL)

        # response should return a HTTP_200_OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check the length of the response returned is 1
        self.assertEqual(len(response.data), 1)
        # check that the name of the tag is the
        # one that we created and assigned to the user
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""

        payload = {'name': 'Cabbage'}

        self.client.post(INGREDIENTS_URL, payload)

        # filter anything that belongs to the authenticated user
        # with the name Carbage
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
