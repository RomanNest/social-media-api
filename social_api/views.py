from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    extend_schema_view,
)
from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from social_api.models import Post, Comment, Like, Follow
from social_api.serializers import (
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    LikeSerializer,
    LikeCreateSerializer,
    LikeListSerializer,
    FollowSerializer,
    FollowListSerializer,
    FollowRetrieveSerializer,
)


@extend_schema_view(
    create=extend_schema(
        summary="Create a new post",
        description="User can create a new post.",
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about a specific post.",
        description="User can get a detailed info about a specific post.",
    ),
    update=extend_schema(
        summary="Update an info about a specific post",
        description="User can a partial update of own post or admin can any.",
    ),
    destroy=extend_schema(
        summary="Delete a post.",
        description="User can delete own post or admin any.",
    )
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "add_comment":
            return CommentCreateSerializer
        if self.action == "add_like":
            return LikeCreateSerializer
        if self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get("username")
        title = self.request.query_params.get("title")
        hashtag = self.request.query_params.get("hashtag")
        like = self.request.query_params.get("like")

        if username:
            queryset = queryset.filter(author__username__icontains=username)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if hashtag:
            queryset = queryset.filter(hashtag__icontains=hashtag)
        if like:
            queryset = queryset.filter(likes__gte=like)
        if self.action in ("list", "retrieve"):
            return queryset.select_related("author")
        return queryset

    @extend_schema(
        methods=["GET"],
        summary="Get list of all posts",
        description="User can get a list of all posts.",
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter by post author username",
                type=OpenApiTypes.STR,
                examples=[OpenApiExample("Example")],
            ),
            OpenApiParameter(
                name="title",
                description="Filter by post title",
                type=OpenApiTypes.STR,
                examples=[OpenApiExample("Example")],
            ),
            OpenApiParameter(
                name="hashtag",
                description="Filter by post hashtag",
                type=OpenApiTypes.STR,
                examples=[OpenApiExample("Example")],
            ),
            OpenApiParameter(
                name="likes",
                description="Filter by post likes",
                type=OpenApiTypes.STR,
                examples=[OpenApiExample("Example")],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Add a comment to a specific post",
        description="User can add a comment to a specific post.",
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="add-comment",
    )
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data,
            context={"request": request, "post_id": pk, "user": request.user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Add the like to the specific post",
        description="User can add a like to a specific post.",
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="add-like",
    )
    def add_like(self, request, pk=None):
        post = self.get_object()
        serializer = LikeCreateSerializer(
            data=request.data,
            context={"request": request, "post_id": pk, "user": request.user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Unlike a specific post",
        description="User can unlike a specific post.",
    )
    @action(detail=True, methods=["post"], url_path="unlike-post",)
    def unlike_post(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like = Like.objects.filter(post=post, user=request.user)
        like.delete()
        return Response(
            {"detail": "Unliked post."},
            status=status.HTTP_204_NO_CONTENT
        )


@extend_schema_view(
    create=extend_schema(
        summary="Create a new comment",
        description="User can create a new comment.",
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about a specific comment.",
        description="User can get a detailed info about a specific comment.",
    ),
    update=extend_schema(
        summary="Update an info about a specific comment.",
        description="User can update an info about a specific comment.",
    ),
    destroy=extend_schema(
        summary="Delete a comment.",
        description="User can delete own comment.",
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve",):
            return queryset.select_related("user", "post")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        methods=["GET"],
        summary="Get list of all comments",
        description="User can get a list of all comments",

    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    destroy=extend_schema(
        summary="Delete a Like.",
        description="Admin can delete own Like.",
    ),
    create=extend_schema(
        summary="Create a new Like.",
        description="User can create a new Like.",
    )
)
class LikeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return LikeListSerializer
        return LikeCreateSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FollowListSerializer
        return FollowRetrieveSerializer

    def get_queryset(self):
        queryset = self.queryset
        follower = self.request.query_params.get("follower")
        following = self.request.query_params.get("following")
        if follower:
            queryset = queryset.filter(follower__username__icontains=follower)
        if following:
            queryset = queryset.filter(
                following__username__icontains=following
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related("follower", "following")
        return queryset

    @extend_schema(
        methods=["GET"],
        summary="Get list of all follows",
        description="User can get a list of all follows",
        parameters=[
            OpenApiParameter(
                name="follower",
                description="Filter by follower username",
                type=str,
                examples=[OpenApiExample("example")]
            ),
            OpenApiParameter(
                name="following",
                description="Filter by following username",
                type=str,
                examples=[OpenApiExample("example")]
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FollowUserView(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    @extend_schema(
        methods=["POST"],
        summary="Follow a specific user.",
        description="User can follow a specific user.",
    )
    def post(self, request, *args, **kwargs):
        username = kwargs.get("username")
        following = get_object_or_404(get_user_model(), username=username)
        follower = request.user
        follow_data = {"follower": follower.id, "following": following.id}
        serializer = self.get_serializer(data=follow_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Follow successful."}, status=status.HTTP_201_CREATED
        )


class UnfollowUserView(generics.GenericAPIView, mixins.DestroyModelMixin):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    @extend_schema(
        methods=["DELETE"],
        summary="Unfollow a specific user.",
        description="User can unfollow a specific user.",
    )
    def delete(self, request, *args, **kwargs):
        username = kwargs.get("username")
        following = get_object_or_404(get_user_model(), username=username)
        follower = request.user
        follow_instance = Follow.objects.filter(
            follower=follower, following=following
        ).first()
        if follow_instance:
            follow_instance.delete()

        return Response(
            {"detail": "Unfollow successful."},
            status=status.HTTP_204_NO_CONTENT,
        )
