from django.contrib import admin

from social_api.models import Follow, Comment, Like, Post


admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Post)
