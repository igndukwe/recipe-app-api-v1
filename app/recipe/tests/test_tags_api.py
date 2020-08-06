from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

# ../recipe/tag-list
TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        # setup the client
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        # get this url ../recipe/tag-list
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        # same user enter two tag objects 'Vegan' and 'Dessert'
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # get this url ../recipe/tag-list
        # with 2 tags returnd to the response list
        response = self.client.get(TAGS_URL)

        # -name ensures that tags are returned in reverse order
        # or alphabetical order based on the name
        tags = Tag.objects.all().order_by('-name')

        # many=True: becos there is more than one item in serializer
        serializer = TagSerializer(tags, many=True)

        # response should return a HTTP_200_OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # response.data is data tat was returned in the response
        # serializer.data is data returned from the database
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )

        # create a Tag object with user2
        Tag.objects.create(user=user2, name='Fruity')

        # create a Tag object with initially created user in the setUp() mtd
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        # get this url ../recipe/tag-list
        # with 1 tag returnd to the response list
        response = self.client.get(TAGS_URL)

        # response should return a HTTP_200_OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check the length of the response returned is 1
        self.assertEqual(len(response.data), 1)
        # check that the name of the tag is the
        # one that we created and assigned to the user
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""

        # create a tag payload
        payload = {'name': 'Simple'}

        # do a HTTP POST the payload
        self.client.post(TAGS_URL, payload)

        # check if the Tag with name 'Simple' exists
        # filter all tags with the authenticated user
        # it will return a boolean True or False
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        # Test will fail if this does not exis
        self.assertTrue(exists)

    # see what happens if we create a tag with invalied string
    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        # payload with an empty name
        payload = {'name': ''}

        # do a HTTP POST the payload
        response = self.client.post(TAGS_URL, payload)

        # returns a bad request becos empty string does not exist
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
