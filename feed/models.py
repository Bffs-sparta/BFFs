from django.conf import settings
from django.db import models
from django.utils import timezone
from hitcount.models import HitCountMixin

from community.models import Community
from user.models import User, Profile

import os
from uuid import uuid4


# 일반 feed 모델
class Feed(models.Model, HitCountMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author"
    )
    category = models.ForeignKey(
        "feed.Category",
        on_delete=models.CASCADE,
        related_name="feed_category",
        blank=False,
    )
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="media/photo/%Y/%m/%d", null=True, blank=True)
    video = models.FileField(upload_to="media/video/%Y/%m/%d", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        "user.User", blank=True, default=[], related_name="feed_likes"
    )
    is_notification = models.BooleanField(default=False)

    # 조회수 코드
    view_count = models.PositiveIntegerField(default=0)

    @property
    def click(self):
        self.view_count += 1
        self.save()

    class Meta:
        verbose_name = "일반 게시글(Feed)"
        verbose_name_plural = "일반 게시글(Feed)"


# community 내 feed에 대한 카테고리 모델, 전체/자유/모집/공구
class Category(models.Model):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="community_category"
    )
    category_name = models.CharField(max_length=20)
    category_url = models.CharField(max_length=20)

    class Meta:
        verbose_name = "커뮤니티 카테고리(Category)"
        verbose_name_plural = "커뮤니티 카테고리(Category)"

    def __str__(self):
        return self.category_name


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

    class Meta:
        verbose_name = "댓글(Comment)"
        verbose_name_plural = "댓글(Comment)"

    def __str__(self):
        return self.text


# 대댓글 모델
class Cocomment(models.Model):
    comment = models.ForeignKey(
        Comment, related_name="cocomment", on_delete=models.CASCADE, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cocomment_author",
    )
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "대댓글(Cocomment)"
        verbose_name_plural = "대댓글(Cocomment)"

    def __str__(self):
        return self.text


# 공구 게시글
class GroupPurchase(models.Model, HitCountMixin):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    product_name = models.CharField(max_length=50)
    product_number = models.PositiveIntegerField(default=0, help_text="구매 예상 수량")
    product_price = models.PositiveIntegerField(help_text="전체 금액")
    # product_division_price = models.PositiveIntegerField(help_text="전체 금액/구매 인원수")
    link = models.CharField(max_length=300, null=True, help_text="어떤 물건인지 링크 넣어주기")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ended = models.BooleanField(default=False, help_text="공구 끝내기")

    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="글 작성자")
    person_limit = models.PositiveIntegerField(
        default=0, help_text="공구 제한 인원, 자기자신을 빼고 입력"
    )

    location = models.CharField(max_length=100, help_text="만날 위치")
    meeting_at = models.DateTimeField(help_text="공구 성공 후 만날 시간")
    open_at = models.DateTimeField(null=False, help_text="모집 시작")
    close_at = models.DateTimeField(null=True, help_text="모집 종료")
    END_CHOICES = (
        ("continue", "공구를 계속 진행할 거예요"),
        ("quit", "공구를 진행 하지 않을 거예요"),
        ("discuss", "신청한 사람과 논의 후 결정할래요"),
        ("maybe", "종료 후 고민해보고 결정할래요"),
    )
    end_option = models.CharField(choices=END_CHOICES, max_length=8)

    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="community_purchases"
    )
    category = models.ForeignKey(
        "feed.Category",
        on_delete=models.CASCADE,
        related_name="purchase_category",
        blank=False,
        default=3,
    )

    # 조회수 코드
    view_count = models.PositiveIntegerField(default=0)

    @property
    def click(self):
        self.view_count += 1
        self.save()

    class Meta:
        verbose_name = "공구 게시글(GroupPurchase)"
        verbose_name_plural = "공구 게시글(GroupPurchase)"

    def __str__(self):
        return f"만날 장소 : {str(self.location)} | 모집 인원 : {str(self.person_limit)}명 | 공구 물건 : {str(self.product_name)}"

    def check_end_person_limit_point(self, grouppurchase_id):
        """공구 제한 인원이 채워질 경우 공구 종료"""
        purchasefeed = GroupPurchase.objects.get(id=grouppurchase_id)
        if purchasefeed.joined_user is None:
            print("아직 신청 인원이 없음")
            return False
        else:
            joined = purchasefeed.joined_user.count()
            person_count = self.person_limit - joined
            if person_count <= 0:
                self.is_ended = True
                self.save()
                return True
            else:
                return False

    def check_end_time_limit_point(self):
        """cron을 사용하여 ended_at=기간이 지났을 경우 모집 종료"""
        pass


# 공구에 참여한 유저 모델
class JoinedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    grouppurchase = models.ForeignKey(
        GroupPurchase, on_delete=models.CASCADE, related_name="joined_user"
    )
    product_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, help_text="공구 참여했다가 빠진 경우")

    class Meta:
        verbose_name = "공구 지원자 현황(JoinedUser)"
        verbose_name_plural = "공구지원자 현황(JoinedUser)"

    def __str__(self):
        return f"실명 :{self.profile.user.name} ({self.profile.region})"


def change_image_name(instance, filename):
    ext = os.path.splitext(filename)[-1]
    filename = "feed/BFF_%s%s" % (uuid4().hex, ext)
    return filename


class Image(models.Model):
    image = models.ImageField(upload_to=change_image_name)

    def save(self, *args, **kwargs):
        if self.image:
            new_name = change_image_name(self, self.image.name)
            self.image.name = new_name
        super(Image, self).save(*args, **kwargs)
