from django.db import models


# Requirments to extend the django user model
# while making use of some of the features that come with django
# user model out of the box
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.conf import settings

# provide helper functions
# for creating a user or super user


class UserManager(BaseUserManager):

    # password=None: in case you want to create a user that is not active,
    #  with no password
    # **extra_fildes: take any of the extra fileds that passed in
    # when you create a user
    def create_user(self, email, password=None, **extra_fildes):
        """Creates and saves a new user
        """
        if not email:
            raise ValueError("Users must have an email address")
        # normalize_email(): ensures that the email domain
        # (everything after the "@") is lowercase
        user = self.model(email=self.normalize_email(email), **extra_fildes)
        user.set_password(password)  # password need to be encrypted
        # _db is required for supporting multiple databases
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# gives us all the features that comes out of the box with django user model
# which we can build on top of and customise to fit our usecase
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of user
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # creates a new user manager for our object
    objects = UserManager()

    # By default the username field is username
    # and we have customized it to email
    USERNAME_FIELD = "email"

    # superuser and staff is included
    # as part of the PermissionsMixin


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # instead of referencing the User object directly
        # i.e. User,
        # We wll use the best practice mtd of retrieving
        # the auth user model setting from the django settings.py
        settings.AUTH_USER_MODEL,
        # this means if you delete this user,
        # delete the tags as well
        on_delete=models.CASCADE,
    )

    # string representation of the model
    def __str__(self):
        return self.name


class Ingredient(models.Model):

    """Ingredient to be used in a recipe
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title
