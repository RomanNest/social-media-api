from rest_framework import serializers

from social_api.models import Post, Follow, Like, Comment


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "hashtag",
            "created_at",
            "images",
        )


class PostListSerializer(PostSerializer):
    author = serializers.ReadOnlyField(source="author.email", read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    comments = serializers.IntegerField(
        source="comments.count",
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "created_at",
            "comments",
            "likes",
            "hashtag",
        )


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField(source="post.title", read_only=True)
    user = serializers.ReadOnlyField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "content", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "content", "created_at")


class CommentForRetrievePostSerializer(CommentCreateSerializer):
    user = serializers.ReadOnlyField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("user", "content", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField(source="post.title", read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")


class LikeListSerializer(LikeSerializer):
    user = serializers.ReadOnlyField(source="user.username", read_only=True)
    post = serializers.ReadOnlyField(source="post.title", read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")


class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "created_at")


class LikeRetrieveSerializer(LikeListSerializer):
    user = serializers.ReadOnlyField(source="user.username", read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user", "created_at")


class PostRetrieveSerializer(serializers.ModelSerializer):
    comments = CommentForRetrievePostSerializer(many=True, read_only=True)
    likes = LikeRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "created_at",
            "hashtag",
            "images",
            "comments",
            "likes",
        )


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")

    def validate(self, attrs):
        Follow.unique_follow(
            attrs["follower"].username,
            attrs["following"].username,
            serializers.ValidationError,
        )
        return attrs


class FollowListSerializer(FollowSerializer):
    follower = serializers.CharField(
        source="follower.username",
        read_only=True,
    )
    following = serializers.ReadOnlyField(
        source="following.username",
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = ("id", "follower", "following")


class FollowRetrieveSerializer(FollowListSerializer):
    class Meta:
        model = Follow
        exclude = ["id"]
