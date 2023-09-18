from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.exceptions import ValidationError, BadRequest
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
import requests
from rest_framework import status
from json.decoder import JSONDecodeError
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, RefreshToken
from rest_framework.response import Response
from . import serializers

User = get_user_model()


@api_view(["GET"])
def google_login(request):
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    # fmt:off
    scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    # fmt: on
    redirect_uri = "http://127.0.0.1:8000/api/v1/users/auth/google/callback"
    google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"

    response = redirect(
        f"{google_auth_api}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    )

    return response


@api_view(["GET"])
def google_callback(request):
    code = request.GET.get("code")
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    grant_type = "authorization_code"
    state = "random_string"
    redirection_uri = "http://127.0.0.1:8000/api/v1/users/auth/google/callback"

    google_token_api = f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type={grant_type}&redirect_uri={redirection_uri}&state={state}"

    token_response = requests.post(google_token_api)
    if not token_response.ok:
        raise ValidationError("토큰이 유효하지 않습니다.")

    access_token = token_response.json().get("access_token")
    user_info_response = requests.get(
        f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}",
    )

    if not user_info_response.ok:
        raise ValidationError("유저 정보를 가져올 수 없습니다.")

    user_info = user_info_response.json()

    user_profile = {
        "email": user_info.get("email", ""),
        "name": user_info.get("name", ""),
        "gender": user_info.get("gender", ""),
        "nickname": user_info.get("nickname", ""),
        "profileImge": user_info.get("picture", None),
    }

    try:
        user = User.objects.get(email=user_profile["email"])
    except User.DoesNotExist:
        user = None
    if user is not None:
        if user.login_method != User.LOGIN_GOOGLE:
            raise BadRequest("잘못된 요청입니다.")
    else:
        user = User(
            email=user_profile["email"],
            name=user_profile["name"],
            nickname=user_profile["nickname"],
            profileImg=user_profile["profileImge"],
            login_method=User.LOGIN_GOOGLE,
        )
        user.set_unusable_password()
        user.save()
    token = TokenObtainPairSerializer.get_token(user)
    refresh_token = str(token)
    access_token = str(token.access_token)
    print(user, refresh_token, access_token)
    res = Response(
        {
            "user": user,
            "message": "로그인 성공",
            "token": {
                "access": access_token,
                "refresh": refresh_token,
            },
        },
        status=status.HTTP_200_OK,
    )

    res.set_cookie("access", access_token, httponly=True)
    res.set_cookie("refresh", refresh_token, httponly=True)
    login(
        request,
        user,
        backend="rest_framework_simplejwt.authentication.JWTAuthentication",
    )
    return Response({"message": "구글 로그인이 되었습니다."}, status=status.HTTP_200_OK)
