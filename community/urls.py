from django.urls import path
from . import views

from rest_framework.generics import ListAPIView
from user.models import User
from .serializers import SearchUserSerializer

urlpatterns = [
    path("", views.CommunityView.as_view(), name="community"),
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
]
