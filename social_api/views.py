from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from social_api.models import Post, Comment, Like, Follow
from social_api.serializers import (
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    LikeSerializer,
    LikeCreateSerializer,
    LikeListSerializer, FollowSerializer,
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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
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


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def get_queryset(self):
        queryset = Follow.objects.all().select_related("follower")
        follower_id = self.request.query_params.get("follower_id")
        if follower_id:
            queryset = queryset.filter(follower_id=follower_id)
        return queryset

    @action(detail=False, methods=["get"])
    def followers(self, request):
        """
        Retrieve the list of followers for the authenticated user.
        """
        user = request.user
        followers = Follow.objects.filter(following=user)
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def following(self, request):
        """
        Retrieve the list of users followed by the authenticated user.
        """
        user = request.user
        following = Follow.objects.filter(follower=user)
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)
