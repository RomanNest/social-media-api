from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from user.serializers import UserSerializer, UserRetrieveSerializer


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


class UserListView(generics.ListAPIView):
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

    def list(self, request, *args, **kwargs):
        """Get list of buses"""
        return super().list(request, *args, **kwargs)
