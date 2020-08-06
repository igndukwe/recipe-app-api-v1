# import serializer from the rest framework
from rest_framework import serializers

# import our Tag model
from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        # the model class we want to communicate with
        model = Tag

        # fields to display
        fields = ('id', 'name')

        # make the id read only
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)
