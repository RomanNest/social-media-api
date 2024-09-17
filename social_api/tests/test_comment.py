from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from social_api.models import Post, Comment
from social_api.serializers import CommentSerializer


COMMENT_URL = reverse("social_api:comment-list")


def detail_url(comment_id):
    return reverse("social_api:comment-detail", args=(comment_id,))


class UnauthenticatedCommentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COMMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCommentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.user_1 = get_user_model().objects.create_user(
            email="test_1@test.test", password="testpassword_1"
        )
        self.client.force_authenticate(user=self.user)

        self.post = Post.objects.create(
            author=self.user,
            title="test",
            content="test",
            hashtag="#test"
        )
        self.comment = Comment.objects.create(
            user=self.user, post=self.post, content="test",
        )
        self.comment_1 = Comment.objects.create(
            user=self.user_1, post=self.post, content="test_1",
        )

    def test_comment_list(self):
        res = self.client.get(COMMENT_URL)
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(res.data["results"], serializer.data)
        else:
            self.assertEqual(res.data, serializer.data)

    def test_retrieve_comment_detail(self):
        res = self.client.get(detail_url(self.comment.id))
        serializer = CommentSerializer(self.comment)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
