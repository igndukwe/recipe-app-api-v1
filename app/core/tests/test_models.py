from django.test import TestCase

from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful
        """

        email = "anyi1ta1@gmail.com"
        password = "1234abcd"

        # create a user
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        # check username is correct
        self.assertEqual(user.email, email)
        # check password is correct
        self.assertTrue(user.check_password(password))
