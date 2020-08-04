from django.contrib.auth import get_user_model, authenticate
# Whenever you output any msgs on screen in the python code
# it will be a good idea to pass it through this translation system
# so if you add extra languages to your project
# you can simply add the language file to convert to appropriate language
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object
    """

    class Meta:
        # get_user_model returns the user model class
        model = get_user_model()
        # these are the fields we are making accessible
        fields = ('email', 'password', 'name')
        # ensues that password is write only and a minimum of 5 characters
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # override the create function
    def create(self, validated_data):
        """Create a new user with encrypted password and return it
        """
        # **validated_data passes all JSON from the http POST to create user
        #
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it
        """
        # pop removes the password from the original dict
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user
        """
        # retrive email and password from the attributes
        email = attrs.get('email')
        password = attrs.get('password')

        # authenticate user
        user = authenticate(
            # access context of the request
            request=self.context.get('request'),
            username=email,
            password=password
        )

        # if authentication fails
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        # set our user in the attributes
        attrs['user'] = user

        # return attributes
        return attrs
