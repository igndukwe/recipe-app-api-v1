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
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


# import the Tag model class
from core.models import Tag, Ingredient

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
        # 'queryset = Tag.objects.all()' or'queryset = Ingredient.objects.all()'
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
