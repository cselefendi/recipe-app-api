from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """ Test that new user can be created with email """

        test_username = "teszteles"
        test_email = f"{test_username}@bszu.dev"
        test_password = 'testpass@123'

        user = get_user_model().objects.create_user(
            email=test_email,
            password=test_password
        )

        self.assertEqual(user.email, test_email)
        self.assertTrue(user.check_password(test_password))
