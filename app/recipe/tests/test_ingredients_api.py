from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """ Test the publicly available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to access this endpoint """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ Test the authorized user ingredients API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@bszu.dev',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Test retrieving ingredients for user """

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test that ingredients returned are
        for the authenticated user only """

        user2 = get_user_model().objects.create_user(
            email='masodik_test@bszu.dev',
            password='23pass1234&'
        )

        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=user2, name='Valami mas')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(
            user=self.user
        ).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(ingredients))
        self.assertEqual(res.data, serializer.data)

    def test_create_ingredient_succesful(self):
        """ Test creating a new ingredient """
        payload = {'name': 'Test ingredient'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_not_created_with_invalid(self):
        """ Test creating a new ingredient with invalid payload """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """ Test filtering ingredients by those assigned to recipes """
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Ingredient1'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Ingredient2'
        )
        recipe = Recipe.objects.create(
            user=self.user,
            title="Rec1",
            time_minutes=20,
            price=Decimal('4.85')
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_unique(self):
        """ Test that ingredient will be unique in the returned data """
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Ingredient1'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Ingredient2'
        )
        recipe1 = Recipe.objects.create(
            user=self.user,
            title="Rec1",
            time_minutes=20,
            price=Decimal('4.85')
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Rec2",
            time_minutes=20,
            price=Decimal('4.85')
        )

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)

        self.assertIn(serializer1.data, res.data)
        self.assertEqual(len(res.data), 1)  # unique results
