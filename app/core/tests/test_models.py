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

    def test_new_user_email_normalized(self):
        """ Test that email for new user will be converted to lowercase """

        for test_username in ['teszteles1', 'Teszteles2',
                              'teszTELES3', 'TESZTELES4']:
            test_email = f"{test_username}@bszu.dev"
            test_password = 'testpass@123'

            user = get_user_model().objects.create_user(
                email=test_email,
                password=test_password
            )

            self.assertEqual(user.email, test_email.lower())
            self.assertTrue(user.check_password(test_password))

    def test_new_user_invalid_email(self):
        """ Test that email without email cannot be created """

        with self.assertRaises(ValueError):
            test_email = None
            test_password = 'testpass@123'

            get_user_model().objects.create_user(
                email=test_email,
                password=test_password
            )
