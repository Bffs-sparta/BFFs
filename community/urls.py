from django.urls import path
from . import views
from feed import views as feedviews

from rest_framework.generics import ListAPIView
from user.models import User
from .serializers import SearchUserSerializer

urlpatterns = [
    path("", views.CommunityView.as_view(), name="community_view"),
    path(
        "<str:community_name>/",
        views.CommunityView.as_view(),
        name="community_detail_view",
    ),
    path(
        "<str:community_name>/subadmin/",
        views.CommunitySubAdminView.as_view(),
        name="community_subadmin_view",
    ),
    path(
        "<str:community_name>/forbidden/",
        views.CommunityForbiddenView.as_view(),
        name="community_forbidden_view",
    ),
    path(
        "<str:community_name>/bookmark/",
        views.CommunityBookmarkView.as_view(),
        name="community_bookmark_view",
    ),
    path("search/", views.SearchCommunityView.as_view(), name="search_community_view"),
    path("searchuser/", views.SearchUserView.as_view(), name="search_user_view"),
    # feed 전체 list get
    path(
        "<str:community_name>/list/",
        feedviews.FeedListView.as_view(),
        name="feed_list_view",
    ),
    # feed 카테고리 list get
    path(
        "<str:community_name>/<int:category_id>/",
        feedviews.FeedCategoryListView.as_view(),
        name="feed_category_list_view",
    ),
    # feed 상세, comment get
    path(
        "<str:community_name>/<int:feed_id>/",
        feedviews.FeedDetailView.as_view(),
        name="feed_detail_view",
    ),
    # like 설정/취소
    path("<int:feed_id>/likes/", feedviews.LikeView.as_view(), name="like_view"),
    # feed 게시글 공지 설정/취소
    path(
        "<int:feed_id>/notification/",
        feedviews.FeedNotificationView.as_view(),
        name="feed_notification_view",
    ),
    # grouppurchase 전체 list
    path(
        "<str:community_name>/grouppurchase/",
        feedviews.GroupPurchaseListView.as_view(),
        name="grouppurchase_list_view",
    ),
    # grouppurchase 상세 페이지
    path(
        "<str:community_name>/grouppurchase/<int:grouppurchase_id>/",
        feedviews.GroupPurchaseDetailView.as_view(),
        name="grouppurchase_detail_view",
    ),
    # grouppurchase 참여 / 취소
    path(
        "<int:grouppurchase_id>/join/",
        feedviews.GroupPurchaseJoinedUserView.as_view(),
        name="grouppurchase_join_view",
    ),
]
