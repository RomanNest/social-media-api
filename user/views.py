from django.contrib.auth import get_user_model, logout
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.serializers import UserSerializer, UserRetrieveSerializer, UserLogOutSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserRetrieveSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        email = self.request.query_params.get("email",)
        username = self.request.query_params.get("username",)
        bio = self.request.query_params.get("bio",)

        if email:
            queryset = queryset.filter(email__icontains=email)
        if username is not None and username != "":
            queryset = queryset.filter(username__icontains=username)
        if bio is not None and bio != "":
            queryset = queryset.filter(bio__icontains=bio)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by email (ex ?email=<EMAIL>)",
            ),
            OpenApiParameter(
                name="username",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by username (ex ?username=<USERNAME>)",
            ),
            OpenApiParameter(
                name="bio",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by bio (ex ?bio=<BIO>)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of users"""
        return super().list(request, *args, **kwargs)


class UserDetailView(ModelViewSet):
    serializer_class = UserRetrieveSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model()
    lookup_field = "username"

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Get info about user (ex user/<USERNAME>)",
                type=OpenApiTypes.STR,

            )
        ]

    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return get_user_model().objects.prefetch_related(
            "user_followers", "user_following",
        )


class LogOutUserView(generics.GenericAPIView):
    serializer_class = UserLogOutSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.save()
        return Response(
            {"status": "You have logged out"},
            status=status.HTTP_204_NO_CONTENT,
        )
