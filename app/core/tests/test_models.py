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

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized
        """
        email = 'test@LONDONAPPDEV.COM'
        user = get_user_model().objects.create_user(
            email, 'test123'
        )

        # make all emails lowercase
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalied_email(self):
        """Test_creating user with no email raises error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None, 'test123'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            'test@londonappdev.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
