# pkg for creating temp files
import tempfile
# to create file paths on the system
import os

# pillow requirement
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
# reverse is for generating the urls
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


# recipe => app
# recipe-list => identifier of the app in the url
# ../recipe/recipe-list
RECIPES_URL = reverse('recipe:recipe-list')

# Helper functions


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

# id of the recipe we want to retrive the detail for
# e.g. if the list url is ../api/recipe/recipe_list/
# then the dtail url for recipe with id 1 will be
# ../api/recipe/recipe_list/1/


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""

        # create a sample recipe using the sample_recipe() mtd
        recipe = sample_recipe(user=self.user)

        # add a tag to the recipe
        # this is how to add in a many-to-many relationship
        recipe.tags.add(sample_tag(user=self.user))

        # add an ingredient to the recipe
        recipe.ingredients.add(sample_ingredient(user=self.user))

        # generate the url we are going to call
        url = detail_url(recipe.id)

        # HTTP GET call
        response = self.client.get(url)

        # serielizer
        serializer = RecipeDetailSerializer(recipe)

        # assert that response.data is equals to serializer.data
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        # basic min fields required for creating a recipe
        payload = {
            'title': 'Chocolate cheesecakw',
            'time_minutes': 30,
            'price': 10.00,
        }

        # make the HTTP POST
        response = self.client.post(RECIPES_URL, payload)

        # This is the STD HTTP response status code
        # for creating an object in the REST API
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # retrieve the created recipe from our models
        # > when you create an object using the django rest framework
        #   the default behaviour is that it would return a dic
        #   containing the created object
        # hene response.data['id'] retireves the id key of created object
        #
        recipe = Recipe.objects.get(id=response.data['id'])
        # hence we loop through each one of the keys
        # e.g. {'title': 'Cho', 'time_minutes':30, 'price': 5.00}
        for key in payload.keys():
            # hence check that its the correct values assigned to our model
            # getattr(recipe, key) => recipe.title, recipe.time_minutes ...
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        # create two tags, tag1 and tag2
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')

        # create a payload with fields to create a sample recipe
        payload = {
            'title': 'Avocado lime cheescake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 10.00
        }

        # Make a HTTP POST request to POST payload
        response = self.client.post(RECIPES_URL, payload)

        # response.status_code should return 201 for object created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # retrieve the HTTP object that was created
        recipe = Recipe.objects.get(id=response.data['id'])

        # retrieve the queryset
        # tags that were created with the recipe
        tags = recipe.tags.all()

        # count that the tags returned are two
        # becouse only two tags were created
        self.assertEqual(tags.count(), 2)

        # check if tag1 is found in the list of tags
        self.assertIn(tag1, tags)

        # check if tag2 is found in the list of tags
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        # create two ingredients, ingredient1 and ingredient2
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')

        # create a payload with fields to create a sample recipe
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 45,
            'price': 15.00
        }

        # Make a HTTP POST request to POST payload
        response = self.client.post(RECIPES_URL, payload)

        # response.status_code should return 201 for object created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # retrieve the HTTP object that was created
        recipe = Recipe.objects.get(id=response.data['id'])

        # retrieve the queryset
        # ingredients that were created with the recipe
        ingredients = recipe.ingredients.all()

        # count that the tags returned are two
        # becouse only two tags were created
        self.assertEqual(ingredients.count(), 2)

        # check if ingredient1 is found in the list of ingredients
        self.assertIn(ingredient1, ingredients)

        # check if ingredient2 is found in the list of ingredients
        self.assertIn(ingredient2, ingredients)

    # Remember, during a partial update
    # if you exclude any field
    # then it will not be updated
    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""

        # create a sample recipe using the sample_recipe() mtd
        recipe = sample_recipe(user=self.user)
        # add a tag to the recipie
        recipe.tags.add(sample_tag(user=self.user))
        # create a new tag
        new_tag = sample_tag(user=self.user, name='Curry')

        # payload with all the fields needed to create a recipe
        # hence replace the existing tag with the new tag
        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}

        # create the url with the id to update
        url = detail_url(recipe.id)

        # make the HTTP PATCH request to do a partial update
        self.client.patch(url, payload)

        # update the DB
        recipe.refresh_from_db()

        # assert that the title is equals to the new title
        self.assertEqual(recipe.title, payload['title'])

        # retrieve all tags assigned to this recipe
        tags = recipe.tags.all()

        # check that the lenght of tags is equals to one
        self.assertEqual(len(tags), 1)

        # check that the new tag is in the tag that we retrieved
        self.assertIn(new_tag, tags)

    # Remember, during a full update
    # if you exclude any field
    # then it will be removed after the update
    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        # create a sample recipe using the sample_recipe() mtd
        recipe = sample_recipe(user=self.user)
        # add a tag to the recipie
        recipe.tags.add(sample_tag(user=self.user))

        # create a payload with fields
        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }

        # create the url with the id to update
        url = detail_url(recipe.id)

        # make a HTTP POST Request
        self.client.put(url, payload)

        # refresh from DB to update
        recipe.refresh_from_db()

        # check each field
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        # retrieve all items
        tags = recipe.tags.all()

        # check that the tags assigned is zero
        # because we did not include tags in this update
        # and should be removed
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    # setup authenticated client before test runs
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    # tear down after test runs
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        # creates a temp file at a random location
        # ntf means named temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # create a black square image with dimensions 10 pix
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # a way python reads files
            ntf.seek(0)
            # multipart tells django we want a form with data
            res = self.client.post(url, {'image': ntf}, format='multipart')

        # refresh DB
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        # check that the path to image exist in the file system
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
