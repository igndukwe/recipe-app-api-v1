# import serializer from the rest framework
from rest_framework import serializers

# import our Tag model
from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        # the model class we want to communicate with
        model = Tag

        # fields to display
        fields = ('id', 'name')

        # make the id read only
        read_only_Fields = ('id',)
