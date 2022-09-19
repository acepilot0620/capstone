from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView

from .serializers import UserSerializer, UserBreifSerializer, FollowerSerializer, FollowingSerializer
from .models import User


# 로그인/회원 가입
class CustomLoginView(LoginView):
    authentication_classes = [BasicAuthentication, ]

class CustomRegisterView(RegisterView):
    authentication_classes = [BasicAuthentication, ]

class UserViewSet(GenericViewSet, ListModelMixin):
    model = User
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset

    def list(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.filter(is_staff=False)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'msg': "관리자만 접근할 수 있습니다."})
    
    @action(detail=False, methods=['get', ], )
    def my_info(self, request,  *args, **kwargs):
        self.queryset = self.request.user
        data = UserSerializer(self.queryset).data
        return Response({'status': status.HTTP_200_OK, 'data': data})
    
    @action(detail=True, methods=['post'])
    def follow(self, request,  *args, **kwargs):
        user = self.get_object()
        current_user = self.request.user
        if user != current_user:
            user.followers.add(current_user)
            return Response({'status': status.HTTP_200_OK, "msg": f"{user.nick_name}님을 팔로우 하였습니다."})
        else:
            return Response({'status': status.HTTP_403_FORBIDDEN, "msg":"본인을 팔로우 할 수 없습니다."})
    
    @action(detail=False, methods=['get', ], serializer_class=FollowingSerializer)
    def followings(self, request,  *args, **kwargs):
        self.queryset = self.request.user
        data = FollowingSerializer(self.queryset).data
        return Response({'status': status.HTTP_200_OK, 'data': data})
    
    @action(detail=False, methods=['get', ], serializer_class=FollowerSerializer)
    def followers(self, request,  *args, **kwargs):
        self.queryset = self.request.user
        data = FollowerSerializer(self.queryset).data
        return Response({'status': status.HTTP_200_OK, 'data': data})
        
