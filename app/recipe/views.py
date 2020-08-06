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
from core.models import Tag

# import the serializer
from recipe import serializers


# Create your views here.
class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the database"""
    # requires authentication to access the Tag
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # select all
    queryset = Tag.objects.all()

    # serializer class
    serializer_class = serializers.TagSerializer

    # override
    # filter object by the authenticated user
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # self.queryset is referencing the 'queryset = Tag.objects.all()'
        # then the filtering is performed in the overriden mtd
        # then order by tag name
        return self.queryset.filter(user=self.request.user).order_by('-name')
