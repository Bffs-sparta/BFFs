from django.contrib import admin
from feed.models import Feed, Comment, Cocomment, Category

admin.site.register(Feed)
admin.site.register(Comment)
admin.site.register(Cocomment)
admin.site.register(Category)
