from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@bszu.dev', password='testpass123'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


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

    def test_create_new_superuser(self):
        """ Test creating a new superuser """

        test_username = "teszteles"
        test_email = f"{test_username}@bszu.dev"
        test_password = 'testpass@123'

        user = get_user_model().objects.create_superuser(
            email=test_email,
            password=test_password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_string_representation(self):
        """ Test tag string representation is as expected """

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients(self):
        """ Test the ingredient string representation """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_string_representation(self):
        """ Test the recipe string representation """

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """ Test that image is saved in the correct location """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(
            instance=None,
            filename='myimage.jpg'
        )

        exp_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)
