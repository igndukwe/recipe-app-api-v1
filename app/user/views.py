from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
# import your serializer
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system
    """
    # call the serializer user class to create a user
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user
    """
    # call the serializer user class to authenticate a user
    serializer_class = AuthTokenSerializer
    # sets the renderer so we can view this endpoint in the browsable
    # with a browsable api
    # e.g. log in using chrome and use the username & password
    # click post and it should return a token
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenicated user
    """
    serializer_class = UserSerializer

    # add the authentication so that user must be authenticated
    # i.e. user do not need to have any special permisions
    # they have to be logged in
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    # override this method
    # to get the model for the logged in user
    def get_object(self):
        """Retrieve and return authenticated user
        """
        return self.request.user
