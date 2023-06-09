from django.urls import path
from feed import views

urlpatterns = [
    # 개별 feed 수정 삭제
    path("<int:feed_id>/", views.FeedDetailView.as_view(), name="feed_detail_view"),
    # comment 수정 삭제
    path(
        "<int:comment_id>/", views.CommentView.as_view(), name="comment_put_delete_view"
    ),
    # cocomment 수정 삭제
    path(
        "<int:comment_id>/",
        views.CocommentView.as_view(),
        name="cocomment_put_delete_view",
    ),
]
