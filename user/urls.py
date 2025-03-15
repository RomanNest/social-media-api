from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from user.views import (
    CreateUserView,
    ManageUserView,
    UserListView,
    UserDetailView, LogOutUserView,
)

from social_api.views import FollowUserView, UnfollowUserView

app_name = "user"


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage_user"),
    path("me/logout/", LogOutUserView.as_view(), name="logout_user"),
    path(
        "users/",
        UserListView.as_view(actions={"get": "list"}),
        name="users_list",
    ),
    path(
        "<str:username>/",
        UserDetailView.as_view(actions={"get": "retrieve"}),
        name="users-detail",
    ),
    path(
        "<str:username>/follow/",
        FollowUserView.as_view(),
        name="follow-user"
    ),
    path(
        "<str:username>/unfollow/",
        UnfollowUserView.as_view(),
        name="unfollow-user",
    )
]
