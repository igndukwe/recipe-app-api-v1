# We want to update our django admin
# so that we can manage our custom user model
# this will give us a nice easy iterface that we can use
# to login and see which users have been created, create users
# or make changes to existing users.

# This is where we want to store all our admin unit test
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        # client
        self.client = Client()
        # admin user
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='abcd1234'
        )
        # admin user is logged into the clint
        self.client.force_login(self.admin_user)

        # normal user
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='abcd1234',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page
        """
        # create url using the reverse() function
        # it accepts app_name:the_url_you_want
        # e.g. admin:core_user_changelist
        # the 'core_user_changelist' URL are defined in the django admin doc
        # hence this will generate the url for us
        url = reverse('admin:core_user_changelist')

        # use our test client to perform a http get request on this url
        res = self.client.get(url)

        # lets run some assertions
        # it also checks that the http response is 200
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
