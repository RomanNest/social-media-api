from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from social_api.models import Post, Comment, Like
from social_api.serializers import PostListSerializer, PostRetrieveSerializer


POST_URL = reverse("social_api:post-list")


def detail_url(post_id):
    return reverse("social_api:post-detail", args=(post_id,))


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
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
        self.post_1 = Post.objects.create(
            author=self.user_1,
            title="about test",
            content="about test",
            hashtag="#about_test"
        )

    def test_posts_list(self):
        post_with_comment = self.post_1

        comment = Comment.objects.create(
            user=self.user,
            post=post_with_comment,
            content="test",
        )

        post_with_comment.comments.add(comment)

        res = self.client.get(POST_URL)
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(res.data["results"], serializer.data)
        else:
            self.assertEqual(res.data, serializer.data)

    def test_filter_post_by_hashtag(self):
        res = self.client.get(POST_URL, {"hashtag": "#test"})
        serializer_1 = PostListSerializer(self.post)
        serializer_2 = PostListSerializer(self.post_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_get_invalid_post(self):
        invalid_id = self.post_1.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_post_detail(self):
        res = self.client.get(detail_url(self.post.id))
        serializer = PostRetrieveSerializer(self.post)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_post(self):
        payload = {
            "author": self.user.id,
            "title": "updated title",
            "content": "updated content",
        }
        res = self.client.put(detail_url(self.post.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_post_forbidden(self):
        payload = {
            "title": "updated title",
            "content": "updated content",
        }
        res = self.client.put(detail_url(self.post_1.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        res = self.client.delete(detail_url(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_post_forbidden(self):
        res = self.client.delete(detail_url(self.post_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment(self):
        payload = {
            "user": self.user.id,
            "post": self.post_1.id,
            "content": "test",
        }
        url = f"/api/v1/social_api/posts/{self.post_1.id}/add-comment/"
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_add_like_post(self):
        payload = {
            "user": self.user.id,
            "post": self.post_1.id,
        }
        url = f"/api/v1/social_api/posts/{self.post_1.id}/add-like/"
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        Like.objects.create(user=self.user, post=self.post_1)
        url = f"/api/v1/social_api/posts/{self.post_1.id}/unlike-post/"
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)


class AdminPostTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.test",
            password="admin",
            is_staff=True,
        )
        self.user_1 = get_user_model().objects.create_user(
            email="test_1@test.test",
            password="testpassword",
        )
        self.client.force_authenticate(user=self.user)

        self.post = Post.objects.create(
            author=self.user,
            title="test",
            content="test",
            hashtag="#test"
        )
        self.post_1 = Post.objects.create(
            author=self.user_1,
            title="about test",
            content="about test",
            hashtag="#about_test",
        )

    def test_admin_can_delete_any_post(self):
        res = self.client.delete(detail_url(self.post_1.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)
