from django.db import models


# Requirments to extend the django user model
# while making use of some of the features that come with django
# user model out of the box
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


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
        # normalize_email() converts the 2nd part of the email to lowercases
        user = self.model(email=self.normalize_email(email), **extra_fildes)
        user.set_password(password)  # password need to be encrypted
        # _db is required for supporting multiple databases
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
