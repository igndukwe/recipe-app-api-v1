

# We are goint to be creating a viewset
# and basing it of the combination of generic viewset
# and we are specifically going to use the list model mixins
# > A django rest frameworke feature
#   where you can pull in different parts of a viewset
#   that we want to use for our application
# > so we only want to take the list model function
#   we do not want to the create, update, delete functions
# > we can achive this be a combination of the
# generic viewset and the list model mixins
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# import the Tag model class
from core.models import Tag, Ingredient, Recipe

# import the serializer
from recipe import serializers


# Create your views here.
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin,):
    """Base viewset for user owned recipe attributes"""
    # requires authentication to access the Tag
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # override get_queryset() mtd for ListModelMixin
    # to filter object by the authenticated user
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # self.queryset is referencing the queryset
        # 'queryset = Tag.objects.all()'
        # or 'queryset = Ingredient.objects.all()'
        # then the filtering is performed in the overriden mtd
        # then order by tag name
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # overide perform_create for CreateModelMixin
    # it allows us to hook into the create proceswe do a create object
    # so that when we fo a create object in our ViewSet
    # the validated serializer will be passed in as a serializer argument
    # and we can perform any modifications that we like
    def perform_create(self, serializer):
        """Create a new Object e.g. Tag or Ingredient
        """
        serializer.save(user=self.request.user)

# Create your views here.


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    # select all
    queryset = Tag.objects.all()
    # serializer class
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    # select all
    queryset = Ingredient.objects.all()
    # serializer class
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""

    # add serializer class
    serializer_class = serializers.RecipeSerializer

    # add the recipe class
    queryset = Recipe.objects.all()

    # add athentication classes
    # so that user must be authenticated to be permited to have access
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # override get_queryset()
    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        # limit the object to the authenticated user
        return self.queryset.filter(user=self.request.user)

    # override get_serializer_class()
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        # ViewSet actions are:
        # list, create, retrieve, update, partial update, and destroy
        # > retrieve is the action used for detailed view
        # The self.action contains the action of the request currently used
        # therefore, check that action currently used is the retrieve action
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # override perform_create()
    def perform_create(self, serializer):
        """Create a new recipe"""
        # viewsets.ModelViewSet allows you to create objects out of the box
        # so the default is that if you assign a serializer_class
        # serializer_class = serializers.RecipeSerializer
        # and its assigned to a model
        # then it knows how to create new objects with that model
        # when you do a HTTP POST
        # > hence what we need to do is to assign authenticated user
        # to that model once it has been created
        serializer.save(user=self.request.user)

    # override the upload_image()
    # -methods=[]: mtd your action will use, 'GET', 'POST', 'PUT', 'PATCH'
    # -detail=True: means use only the detail url to upload images
    # also you will be able to upload images for resipes that already exist
    # -url_path: path name for our urls
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # retrieve the recipe object, based on the ID/PK
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        # check if serializer is valied
        if serializer.is_valid():
            serializer.save()
            # return good response
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # else return invalied response
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
