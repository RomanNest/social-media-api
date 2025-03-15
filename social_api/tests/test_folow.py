from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from social_api.models import Follow
from social_api.serializers import FollowListSerializer

FOLLOW_URL = reverse("social_api:follow-list")


class UnauthenticatedAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FOLLOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFollowApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword", username="yes",
        )
        self.user_1 = get_user_model().objects.create_user(
            email="test_1@test.test", password="testpassword", username="no",
        )
        self.client.force_authenticate(user=self.user)
        self.follow = Follow.objects.create(
            follower=self.user, following=self.user_1
        )
        self.follow_1 = Follow.objects.create(
            follower=self.user_1, following=self.user
        )

    def test_follow_list(self):
        res = self.client.get(FOLLOW_URL)
        follows = Follow.objects.all()
        serializer = FollowListSerializer(follows, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(Follow.objects.count(), 2)

    def test_filter_follower_by_username(self):
        res = self.client.get(FOLLOW_URL, data={"follower": "no"})
        serializer = FollowListSerializer(self.follow)
        serializer_1 = FollowListSerializer(self.follow_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer.data, res.data)

    def test_filter_following_by_username(self):
        res = self.client.get(FOLLOW_URL, data={"following": "no"})
        serializer = FollowListSerializer(self.follow)
        serializer_1 = FollowListSerializer(self.follow_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer_1.data, res.data)

    def test_follow_user(self):
        self.user_2 = get_user_model().objects.create_user(
            email="test_2@test.test", password="password_2", username="hz",
        )
        self.client.force_authenticate(self.user_2)
        url = f"/api/v1/user/{self.user.username}/follow/"
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_unfollow_user(self):
        self.client.force_authenticate(self.user_1)
        url = f"/api/v1/user/{self.user.username}/unfollow/"
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
