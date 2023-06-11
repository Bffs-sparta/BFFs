
from django.contrib import admin
from feed.models import Feed, Comment, Cocomment, Category, GroupPurchase, JoinedUser


admin.site.register(Feed)
admin.site.register(Comment)
admin.site.register(Cocomment)
admin.site.register(Category)
admin.site.register(GroupPurchase)
admin.site.register(JoinedUser)

