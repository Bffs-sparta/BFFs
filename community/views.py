from rest_framework import permissions, status, filters
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# from feed.models import Feed
from user.models import User
from .models import Community, CommunityAdmin, ForbiddenWord
from .serializers import (
    CommunitySerializer,
    CommunityCreateSerializer,
    CommunityUpdateSerializer,
    CommunityAdminCreateSerializer,
    ForbiddenWordSerializer,
    SearchUserSerializer,
)


class CommunityView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """커뮤니티 조회 및 북마크, 어드민 조회"""
        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
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
            {"data": serializer.data, "msg": "커뮤니티 생성 신청이 완료되었습니다."},
            status=status.HTTP_202_ACCEPTED,
        )

    def put(self, request, comu_id):
        """커뮤니티 수정"""
        community = get_object_or_404(Community, id=comu_id)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            serializer = CommunityUpdateSerializer(community, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"data": serializer.data, "msg": "수정이 완료되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"msg": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, comu_id):
        """커뮤니티 삭제"""
        community = get_object_or_404(Community, id=comu_id)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            community.delete()
            return Response({"msg": "삭제가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"msg": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)


class CommunitySubAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comu_id):
        """서브 어드민 등록"""
        community = Community.objects.get(id=comu_id)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            if community.comu.filter(user_id=request.data["user"]).exists():
                return Response(
                    {"msg": "이미 관리자로 등록된 유저입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            elif community.comu.filter(community_id=comu_id).count() > 3:
                return Response(
                    {"msg": "서브 관리자는 최대 3명입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer = CommunityAdminCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(community=community, is_subadmin=True)
                return Response(
                    {"msg": "서브 관리자 등록이 완료되었습니다."}, status=status.HTTP_201_CREATED
                )
        else:
            return Response({"msg": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, comu_id):
        """서브 어드민 삭제"""
        community = Community.objects.get(id=comu_id)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            if community.comu.filter(user_id=request.data["user"]).exists():
                community.comu.filter(user_id=request.data["user"]).delete()
                return Response(
                    {"msg": "서브 관리자 삭제가 완료되었습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"msg": "존재하지 않는 서브 관리자입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response({"msg": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)


class CommunityForbiddenView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, comu_id):
        """커뮤니티 금지어 조회"""
        forbiddenword = ForbiddenWord.objects.filter(community_id=comu_id)
        serializer = ForbiddenWordSerializer(forbiddenword, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, comu_id):
        """커뮤니티 금지어 생성"""
        community = Community.objects.get(id=comu_id)
        community_admin = community.comu.get(is_comuadmin=True).user
        if community_admin == request.user:
            serializer = ForbiddenWordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(community=community)
            return Response({"msg": "등록이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"msg": "권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)


class CommunityBookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comu_id):
        """북마크 등록 및 취소"""
        community = Community.objects.get(id=comu_id)
        if request.user in community.bookmarked.all():
            community.bookmarked.remove(request.user)
            return Response({"msg": "북마크가 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            community.bookmarked.add(request.user)
            return Response({"msg": "북마크가 등록되었습니다."}, status=status.HTTP_200_OK)


class SearchCommunityView(ListAPIView):
    """커뮤니티 조회 및 검색"""

    queryset = Community.objects.all()
    serializer_class = CommunityCreateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]


class SearchUserView(ListAPIView):
    """유저 조회 및 검색"""

    queryset = User.objects.all()
    serializer_class = SearchUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email"]
