from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "username", "is_staff"]
        read_only_fields = ["id", "is_staff"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "min_length": 5,
                "label": _("Password"),
            },
        }

        def create(self, validated_data):
            """Create a new user with encrypted password and return it."""
            return get_user_model().objects.create_user(**validated_data)

        def update(self, instance, validated_data):
            """Update a user, set the password correctly and return it"""
            password = validated_data.pop("password", None)
            user = super().update(instance, validated_data)
            if password:
                user.set_password(password)
                user.save()

            return user


class UserRetrieveSerializer(serializers.ModelSerializer):
    followers = serializers.IntegerField(source="following.count", read_only=True)
    following = serializers.IntegerField(source="follower.count", read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "username",
            "bio",
            "is_staff",
            "followers",
            "following",
            "image",
        ]


class UserLogOutSerializer(serializers.Serializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "min_length": 5,
                "label": _("Password"),
            }
        }
