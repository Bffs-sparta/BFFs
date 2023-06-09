from django.contrib import admin
from feed.models import Feed, Comment, Cocomment, Category

admin.site.register(Feed, Comment, Cocomment, Category)
