from django.contrib import admin
from feed.models import Feed, Comment, Cocomment, Board

admin.site.register(Feed, Comment, Cocomment, Board)
