# import serializer from the rest framework
from rest_framework import serializers

# import our Tag model
from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        # point to the model we want to communicate with
        model = Tag
        # fields to return
        fields = ('id', 'name')
        # make the id read only
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        # point serializer to correct model
        model = Ingredient
        # list the fields to return in our serializer
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""

    # primary key related fields of ingredient
    # lists only the primary key ids
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    # primary key related fields of tag
    # lists only the primary keys
    # can also list RelatedField
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        # point serializer to correct model
        model = Recipe
        # list the fields to return in our serializer
        # > ingredients & tags are references
        # to ingredients & tags model we need to define them
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_minutes', 'price',
            'link',
        )
        # read only fields
        read_only_fields = ('id',)

# Notice that the difference between
# RecipeSerializer and RecipeDetailSerializer
# is that RecipeSerializer returns the Primary Key Related Fields
# i.e the ids of both ingredients and tags associated with our recipe
# > while RecipeDetailSerializer returns the details
# of the ingredients and tags associated with our recipe
# this is call Nesting Serializers inside each other


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail
    """
    # many: means you can have many ingredients associated with a recipie
    # read_only: you can not create a recipe by providing this values
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipe"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
