from django.db.models import Q

from rest_framework import permissions, status, filters
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect


from user.models import User
from user.serializers import SearchUserSerializer
from feed.models import Feed
from .models import Community, CommunityAdmin, ForbiddenWord
from .serializers import (
    CommunitySerializer,
    CommunityCategorySerializer,
    CommunityCreateSerializer,
    CommunityUpdateSerializer,
    CommunityAdminCreateSerializer,
    ForbiddenWordSerializer,
    CommunityListSerializer,
)


class CommunityView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """커뮤니티 조회 및 북마크, 어드민 조회"""
        communities = Community.objects.all().order_by("?")
        serializer = CommunityListSerializer(
            communities, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """커뮤니티 생성 신청시 유저 어드민 등록까지"""
        serializer = CommunityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        community = serializer.save()
        CommunityAdmin.objects.create(
            user=request.user, community=community, is_comuadmin=True
        )
        return Response(
            {"data": serializer.data, "message": "커뮤니티 생성 신청이 완료되었습니다."},
            status=status.HTTP_202_ACCEPTED,
        )


class CommunityDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, community_url):
        """커뮤니티 관리자 페이지에서 조회 및 북마크, 어드민 조회"""
        community = get_object_or_404(Community, communityurl=community_url)
        serializer = CommunitySerializer(community, context={"request": request})
        return Response(
            {"data": serializer.data, "message": "조회가 완료되었습니다."},
            status=status.HTTP_200_OK,
        )

    def put(self, request, community_url):
        """커뮤니티 수정"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user
        community_subadmin = [
            admin.user for admin in community.comu.filter(is_subadmin=True)
        ]
        if community_admin == request.user or request.user in community_subadmin:
            serializer = CommunityUpdateSerializer(community, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "수정이 완료되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, community_url):
        """커뮤니티 삭제"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            community.delete()
            return Response(
                {"message": "삭제가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class CommunityCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, community_url):
        """게시글 작성 페이지에서 커뮤니티 카테고리 조회"""
        community = get_object_or_404(Community, communityurl=community_url)
        serializer = CommunityCategorySerializer(community)
        return Response(
            {"data": serializer.data, "message": "조회가 완료되었습니다."},
            status=status.HTTP_200_OK,
        )


class CommunitySubAdminView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, community_url):
        """어드민 등록을 위한 현재 커뮤니티의 유저를 제외한 전체 유저 조회"""
        community = get_object_or_404(Community, communityurl=community_url)
        try:
            exist_users = community.comu.filter(
                Q(is_comuadmin=True) | Q(is_subadmin=True)
            )
            user_ids = exist_users.values_list("user_id", flat=True)
            try:
                excluded_users = User.objects.all().exclude(id__in=user_ids)
                serializer = SearchUserSerializer(excluded_users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except CommunityAdmin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, community_url):
        """서브 어드민 등록"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user

        if community_admin == request.user:
            if community.comu.filter(user_id=request.data["user"]).exists():
                return Response(
                    {"message": "이미 관리자로 등록된 유저입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif community.comu.filter(community_id=community.id).count() > 3:
                return Response(
                    {"message": "서브 관리자는 최대 3명입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer = CommunityAdminCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(community=community, is_subadmin=True)
                return Response(
                    {"message": "서브 관리자 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED
                )
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, community_url):
        """서브 어드민 삭제"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            if community.comu.filter(user_id=request.data["user"]).exists():
                community.comu.filter(user_id=request.data["user"]).delete()
                return Response(
                    {"message": "서브 관리자 삭제가 완료되었습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "존재하지 않는 서브 관리자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class CommunityForbiddenView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, community_url):
        """커뮤니티 금지어 조회"""
        community = get_object_or_404(Community, communityurl=community_url)
        forbiddenword = ForbiddenWord.objects.filter(community_id=community.id)
        serializer = ForbiddenWordSerializer(forbiddenword, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, community_url):
        """커뮤니티 금지어 생성"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user
        community_subadmin = [
            admin.user for admin in community.comu.filter(is_subadmin=True)
        ]
        if community_admin == request.user or request.user in community_subadmin:
            text = request.data["word"].strip()
            if text not in [
                forbidden.word
                for forbidden in ForbiddenWord.objects.filter(community_id=community.id)
            ]:
                serializer = ForbiddenWordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(community=community)
                return Response(
                    {"message": "등록이 완료되었습니다."}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"message": "이미 등록된 금지어입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, community_url, forbidden_word):
        """커뮤니티 금지어 삭제"""
        community = get_object_or_404(Community, communityurl=community_url)
        community_admin = community.comu.get(is_comuadmin=True).user
        community_subadmin = [
            admin.user for admin in community.comu.filter(is_subadmin=True)
        ]
        if community_admin == request.user or request.user in community_subadmin:
            word = ForbiddenWord.objects.get(
                word=forbidden_word, community_id=community.id
            )
            word.delete()
            return Response({"message": "금지어 삭제가 완료되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class CommunityBookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_url):
        """북마크 등록 및 취소"""
        community = get_object_or_404(Community, communityurl=community_url)
        if request.user in community.bookmarked.all():
            community.bookmarked.remove(request.user)
            return Response({"message": "북마크가 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            community.bookmarked.add(request.user)
            return Response({"message": "북마크가 등록되었습니다."}, status=status.HTTP_200_OK)


class SearchCommunityView(ListAPIView):
    """커뮤니티 조회 및 검색"""

    queryset = Community.objects.all()
    serializer_class = CommunityListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "communityurl", "introduction"]
    pagination_class = None
