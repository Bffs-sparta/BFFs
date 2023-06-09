from django.urls import path
from . import views
from feed import views as feedviews

from rest_framework.generics import ListAPIView
from user.models import User
from .serializers import SearchUserSerializer

urlpatterns = [
    path("", views.CommunityView.as_view(), name="community_view"),
    path("<int:comu_id>/", views.CommunityView.as_view(), name="community_detail_view"),
    path(
        "<int:comu_id>/subadmin/",
        views.CommunitySubAdminView.as_view(),
        name="community_subadmin_view",
    ),
    path(
        "<int:comu_id>/forbidden/",
        views.CommunityForbiddenView.as_view(),
        name="community_forbidden_view",
    ),
    path(
        "<int:comu_id>/bookmark/",
        views.CommunityBookmarkView.as_view(),
        name="community_bookmark_view",
    ),
    path("search/", views.SearchCommunityView.as_view(), name="search_community_view"),
    path("searchuser/", views.SearchUserView.as_view(), name="search_user_view"),
    # feed 전체 list
    path(
        "<str:community_name>/", feedviews.FeedListView.as_view(), name="feed_list_view"
    ),
    # feed 카테고리 list
    path(
        "<str:community_name>/",
        feedviews.FeedCategoryListView.as_view(),
        name="feed_category_list_view",
    ),
    # feed 생성
    path(
        "<str:community_name>/",
        feedviews.FeedCreateView.as_view(),
        name="feed_create_view",
    ),
    # feed 상세, comment, cocoment get
    path(
        "<str:community_name>/<int:feed_id>/",
        feedviews.FeedDetailView.as_view(),
        name="feed_detail_view",
    ),
    # comment 생성
    path(
        "<int:feed_id>/comment_id/",
        feedviews.CommentView.as_view(),
        name="comment_create_view",
    ),
    # 대댓글, cocomment 생성
    path(
        "<int:feed_id>/comment_id/",
        feedviews.CocommentView.as_view(),
        name="cocomment_create_view",
    ),
    # like 성공/취소
    path("<int:feed_id>/likes/", feedviews.LikeView.as_view(), name="like_view"),
]
