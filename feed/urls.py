from django.urls import path
from .views import (
    FeedDetailView,
    FeedCreateView,
    CommentView,
    CommentView,
    CocommentView,
    CocommentView,
    GroupPurchaseCreateView,
    GroupPurchaseDetailView,
)

urlpatterns = [
    # 개별 feed 수정 삭제
    path("<int:feed_id>/", FeedDetailView.as_view(), name="feed_detail_view"),
    # feed 생성
    path(
        "<str:category_name>/feed/",
        FeedCreateView.as_view(),
        name="feed_create_view",
    ),
    # comment 생성
    path(
        "<int:feed_id>/comment/",
        CommentView.as_view(),
        name="comment_create_view",
    ),
    # comment 수정 삭제
    path(
        "comment/<int:comment_id>/",
        CommentView.as_view(),
        name="comment_put_delete_view",
    ),
    # 대댓글, cocomment get 생성
    path(
        "<int:comment_id>/cocomment/",
        CocommentView.as_view(),
        name="cocomment_create_view",
    ),
    # cocomment 수정 삭제
    path(
        "cocomment/<int:cocomment_id>/",
        CocommentView.as_view(),
        name="cocomment_put_delete_view",
    ),
    # grouppurchase 게시글 생성
    path(
        "<str:community_name>/grouppurchase/",
        GroupPurchaseCreateView.as_view(),
        name="grouppurchase_create_view",
    ),
    # grouppurchase 게시글 수정 삭제
    path(
        "grouppurchase/<int:grouppurchase_id>/",
        GroupPurchaseDetailView.as_view(),
        name="grouppurchase_put_delete_view",
    ),
    # grouppurchase 참여 / 취소
    path(
        "<int:grouppurchase_id>/join/",
        GroupPurchaseJoinedUserView.as_view(),
        name="grouppurchase_join_view",
    ),
]
