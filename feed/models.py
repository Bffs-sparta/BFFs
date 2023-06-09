from django.db import models
from hitcount.models import HitCountMixin, HitCount
from django.conf import settings
from user.models import User
from community.models import Community


# 일반 feed 모델
class Feed(models.Model, HitCountMixin):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="community_feeds"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author"
    )
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="media/photo/%Y/%m/%d", null=True, blank=True)
    video = models.FileField(upload_to="media/video/%Y/%m/%d", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        "user.User", blank=True, default=0, related_name="feed_likes"
    )
    is_notification = models.BooleanField(default=False)

    category = models.ManyToManyField(
        "feed.Category", related_name="feed_category", blank=False
    )

    # 조회수 코드
    view_count = models.PositiveIntegerField(default=0)

    @property
    def click(self):
        self.view_count += 1
        self.save()


# 공구 폼
class GroupPurchase(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True)
    product = models.CharField(max_length=50)
    person_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=False)
    ended_at = models.DateTimeField(null=True)
    # 만약 구매기능까지 있으면 = 상품에 대한 db내용도 필요함 / 참여하는 사람들 / 유저 정보 필요함


# community 내 feed에 대한 카테고리 모델, 전체/자유/모집/공구
class Category(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=20)


# 댓글 모델
class Comment(models.Model):
    feed = models.ForeignKey(Feed, related_name="comment", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_author",
    )
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


# 대댓글 모델
class Cocomment(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="cocomment")
    comment = models.ForeignKey(
        Comment, related_name="cocomment", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cocomment_author",
    )
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


# # 댓글 - 자기자신을 참조하는 댓글 모델
# class Comment(models.Model):
#     feed = models.ForeignKey(Feed, related_name='comment', on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_author')
#     comment = models.ForeignKey(Comment, related_name='parent_comment', on_delete=models.SET_NULL, null=True)
#     text = models.CharField(max_length=500)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.text
