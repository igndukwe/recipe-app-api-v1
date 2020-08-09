from django.contrib.auth import get_user_model
from django.test import TestCase
# reverse is for generating the urls
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

# recipe => app
# recipe-list => identifier of the app in the url
# ../recipe/recipe-list
RECIPES_URL = reverse('recipe:recipe-list')

# set up a function that allows us to setup a
# recipe with default values
# this makes things a lot easier
# - **params: parses args into a dic


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    # adds new key/value
    # or updates the values of the keys specified
    defaults.update(params)

    # **defaults: passes a dic into args
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    # setup for unauthenticated user
    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test that authenticaiton is required"""

        # make an unauthenticated request
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    # setup for authenticated user
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        # make an unauthenticated request
        response = self.client.get(RECIPES_URL)

        # request recipie from the database
        recipes = Recipe.objects.all().order_by('-id')
        # pass recipes into serializer
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""

        # create a new user
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'pass'
        )
        # first sample recipe for new user
        sample_recipe(user=user2)

        # first sample recipe for another user
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        # request recipie from the database filter by user
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # it should return just one result
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
