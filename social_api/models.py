import pathlib
import uuid

from django.db import models
from django.utils.text import slugify

from user.models import User


def post_image_file_path(instance: "Post", filename: str) -> pathlib.Path:
    filename = (f"{slugify(instance.title)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path("uploads/posts/", filename)


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def unique_follow(follower: str, following: str, error_to_raise) -> dict:
        if follower == following:
            raise error_to_raise("You can't follow yourself")
        if Follow.objects.filter(
            follower__username=follower, following__username=following
        ).exists():
            raise error_to_raise("You have already followed this user")
        return {"follower": follower, "following": following}

    def clean(self) -> None:
        Follow.unique_follow(
            self.follower.username, self.following.username, ValueError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
            *args,
            **kwargs,
    ):
        self.full_clean()
        super(Follow, self).save(
            force_insert, force_update, using, update_fields,
        )

    def __str__(self):
        return f"{self.follower.username} followed {self.following.username}"

    class Meta:
        ordering = ["-created_at"]


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    hashtag = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(null=True, upload_to=post_image_file_path)

    def __str__(self):
        return f"{self.author.email} crated {self.title} at {self.created_at}"

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def unique_like(user: str, post: str, error_to_raise):
        if Like.objects.filter(user__email=user, post__content=post).exists():
            raise error_to_raise("You have already liked this post.")
        return {"user": user, "post": post}

    def clean(self):
        Like.unique_like(self.user.email, self.post.content, ValueError)

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None,
             *args,
             **kwargs,
             ):
        self.full_clean()
        return super(Like, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self):
        return f"{self.user.email} liked " f"{self.post.id} post"


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} commented {self.post.id}"

    class Meta:
        ordering = ["-created_at"]
