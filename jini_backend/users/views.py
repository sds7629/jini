from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.db.models import Prefetch
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ParseError, NotFound, MethodNotAllowed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from feeds.models import Feed
from . import permissions
from . import serializers


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related(
        Prefetch("feeds", queryset=Feed.objects.all(), to_attr="my_feeds")
    ).all()
    filterset_fields = ("nickname",)
    permission_classes = [AllowAny]

    def get_serializer(self, *args, **kwargs):
        if self.action in ["list"]:
            serializer_class = serializers.ListUserSerializer
        else:
            serializer_class = serializers.UserSerializer
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    @extend_schema(
        tags=["User"],
        description="User",
        summary="유저 pk로 조회하기",
        responses=serializers.UserSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            raise NotFound
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        tags=["User"],
        description="회원 가입",
        summary="회원 가입",
        responses=serializers.CreateUserSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 가입",
                name="Register",
                value={
                    "email": "email",
                    "password": "password",
                    "nickname": "nickname",
                    "gender": "gender",
                    "name": "name",
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # token = TokenObtainPairSerializer.get_token(user)
            # refresh_token = str(token)
            # access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "회원가입 완료.",
                },
                status=status.HTTP_200_OK,
            )
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["사용안함"],
        description="시용안함",
        summary="사용안함",
        responses=serializers.UserSerializer,
    )
    def destroy(self, request, *args, **kwargs):
        return redirect("http://www.jinii.shop/api/v1/users/logout")

    @extend_schema(
        tags=["User"],
        description="로그아웃",
        summary="로그아웃",
        responses=serializers.UserSerializer,
    )
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def logout(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            res = Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
            refresh_token = request.COOKIES.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            res.delete_cookie("access_token")
            res.delete_cookie("refresh_token")
            logout(request)
            return res

    @extend_schema(
        tags=["User"],
        description="로그인",
        summary="로그인",
        responses=serializers.UserSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="로그인",
                name="Register",
                value={
                    "email": "email",
                    "password": "password",
                },
            ),
        ],
    )
    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if user:
            serializer = serializers.LoginSerializer(user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "로그인 성공",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            res.set_cookie("access_token", access_token, httponly=True)
            res.set_cookie("refresh_token", refresh_token, httponly=True)
            login(request, user)
            return res
        return Response({"user": "없는 유저입니다."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["User"],
        description="회원탈퇴",
        summary="회원탈퇴",
        responses=serializers.UserSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원탈퇴",
                name="Register",
                value={
                    "email": "email",
                    "password": "password",
                },
            ),
        ],
    )
    @action(
        methods=["post"],
        detail=False,
        permission_classes=[IsAuthenticated, permissions.IsYour],
    )
    def signout(self, request):
        user = request.user
        if user.is_authenticated:
            request.user.is_active = False
            request.user.save()
            return Response({"message": "회원탈퇴 완료"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=["User"],
    description="마이인포",
    summary="마이인포",
    responses=serializers.ListUserSerializer,
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def get_info(request):
    if request.method == "GET":
        user = request.user
        serializer = serializers.ListUserSerializer(user)
        return Response(serializer.data)
    else:
        queryset = request.user
        serializer = serializers.ListUserSerializer(
            queryset,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        update_user = serializer.save()
        return Response(serializers.ListUserSerializer(update_user).data)


@extend_schema(
    tags=["User"],
    description="이메일 검증",
    summary="이메일 검증",
    examples=[
        OpenApiExample(
            response_only=True,
            summary="이메일 중복",
            name="checker",
            value={
                "email": "email",
            },
        ),
    ],
)
@api_view(["POST"])
def validate_email(request):
    email_data = request.data.get("email")
    if User.objects.filter(email=email_data).exists():
        return Response({"message": "이미 가입된 이메일입니다."}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({"message": "사용 가능한 이메일입니다."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["User"],
    description="닉네임 검증",
    summary="닉네임 검증",
    examples=[
        OpenApiExample(
            response_only=True,
            summary="닉네임",
            name="checker",
            value={
                "nickname": "nicname",
            },
        ),
    ],
)
@api_view(["POST"])
def validate_nickname(request):
    nickname_data = request.data.get("nickname")
    if User.objects.filter(nickname=nickname_data).exists():
        return Response(
            {"message": "이미 사용중인 닉네임입니다."}, status=status.HTTP_403_FORBIDDEN
        )
    else:
        return Response({"message": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["User"],
    description="패스워드 변경",
    summary="패스워드 변경",
    examples=[
        OpenApiExample(
            response_only=True,
            summary="패스워드",
            name="checker",
            value={
                "current_password": "current_password",
                "password_1": "password_1",
                "password_2": "pssword_2",
            },
        ),
    ],
)
@api_view(["POST"])
def change_password(request):
    user = request.user
    current_password = request.data.get("current_password")
    if not check_password(current_password, user.password):
        raise ValidationError({"message": "현재 패스워드가 일치하지 않습니다."})
    new_password = request.data.get("password_1")
    confirm_new_password = request.data.get("password_2")
    if new_password == confirm_new_password:
        user.set_password(new_password)
        user.save()
        return redirect("http://www.jinii.shop")
        # return Response({"message": "ok"})
    else:
        raise ValidationError({"message": "새로운 비밀번호가 일치하지 않습니다."})
