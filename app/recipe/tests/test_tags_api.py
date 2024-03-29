from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """ Test that publicly available tags API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required for retrieving tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ Test the authorized user tags API """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@bszu.dev',
            password='pass1234&'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving tags for user """

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test that tags returned are for the authenticated user only """

        user2 = get_user_model().objects.create_user(
            email='masodik_test@bszu.dev',
            password='23pass1234&'
        )

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=user2, name='Valami mas')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(tags))
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_succesful(self):
        """ Test creating a new tag """
        payload = {'name': 'Test tag'}
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_not_created_with_invalid(self):
        """ Test creating a new tag with invalid payload """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """ Test filtering tags by those assigned to recipes """
        tag1 = Tag.objects.create(user=self.user, name='Tag1')
        tag2 = Tag.objects.create(user=self.user, name='Tag2')
        recipe = Recipe.objects.create(
            user=self.user,
            title="Rec1",
            time_minutes=20,
            price=Decimal('4.85')
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_unique(self):
        """ Test that tag will be unique in the returned data """
        tag1 = Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')
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

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)

        self.assertIn(serializer1.data, res.data)
        self.assertEqual(len(res.data), 1)  # unique results
