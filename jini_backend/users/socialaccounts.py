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
import random
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
    redirect_uri = "http://www.jinii.shop/api/v1/users/auth/google/callback"
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
    redirection_uri = "http://www.jinii.shop/api/v1/users/auth/google/callback"

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
            raise ValidationError(f"{user.login_method}로 로그인 해주세요")
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

    res = Response(
        {
            "user": serializers.ListUserSerializer(user).data,
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
    return res


KAKAO_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_API = "https://kapi.kakao.com/v2/user/me"
KAKAO_CALLBACK_URI = "http://www.jinii.shop/api/v1/users/auth/kakao/callback"


@api_view(["GET"])
def kakao_login(request):
    kakao_api = (
        "https://kauth.kakao.com/oauth/authorize?response_type=code&scope=account_email"
    )
    redirect_uri = "http://www.jinii.shop/api/v1/users/auth/kakao/callback"
    client_id = settings.KAKAO_KEY

    return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}")


@api_view(["GET"])
def kakao_callback(request):
    code = request.GET["code"]

    if not code:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_KEY,
        "redirect_uri": "http://www.jinii.shop/api/v1/users/auth/kakao/callback",
        "code": code,
    }

    token = requests.post("https://kauth.kakao.com/oauth/token", data=data).json()

    access_token = token["access_token"]
    if not access_token:
        return Response(
            {"message": "토큰을 받아오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    headers = {
        "Authorization": f"Bearer ${access_token}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    user_profile = requests.get(KAKAO_USER_API, headers=headers).json()

    # data = {"access_token": access_token, "code": code}
    kakao_account = user_profile.get("kakao_account")

    nickname = kakao_account.get("profile")["nickname"]
    email = kakao_account.get("email")
    profileImg = kakao_account.get("profile")["profile_image_url"]
    gender = kakao_account.get("gender", "")
    name = kakao_account.get("name", "")

    if email is None:
        ValidationError("카카오 계정(이메일) 제공 동의에 체크해 주세요")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = None

    if user is not None:
        if user.login_method != User.LOGIN_KAKAO:
            raise ValidationError(f"{user.login_method}로 로그인 해주세요")
    else:
        # if User.objects.get(nickname=nickname):
        #     rand_num = random.randint(0, 99999)
        #     nickname = f"{nickname}{rand_num}"
        user = User(
            email=email,
            nickname=nickname,
            profileImg=profileImg,
            gender=gender,
            name=name,
            login_method=User.LOGIN_KAKAO,
        )
        user.set_unusable_password()
        user.save()

    token = TokenObtainPairSerializer.get_token(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    res = Response(
        {
            "user": serializers.ListUserSerializer(user).data,
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
    return res


@api_view(["GET"])
def naver_login(request):
    client_id = settings.NAVER_CLIENT_ID
    redierct_uri = "http://www.jinii.shop/api/v1/users/auth/naver/callback"
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={redierct_uri}"
    )


@api_view(["GET"])
def naver_callback(request):
    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    code = request.GET.get("code")
    uri = "http://www.jinii.shop/api/v1/users/auth/naver/callback"
    state_string = request.GET.get("state")

    token_req = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state_string}"
    )
    token_res_json = token_req.json()

    access_token = token_res_json.get("access_token")

    profile_request = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    profile_json = profile_request.json()

    res = profile_json.get("response")

    if res["gender"] == "M":
        gender = "male"
    elif res["gender"] == "F":
        gender = "female"

    data = {
        "email": res["email"],
        "name": res["name"],
        "nickname": res["nickname"],
        "gender": gender,
        "profileImg": res["profile_image"],
    }

    if data["email"] is None:
        raise ValidationError("네이버 계정(이메일) 제공 동의에 체크해 주세요")

    try:
        user = User.objects.get(email=data["email"])
    except User.DoesNotExist:
        user = None

    if user is not None:
        if user.login_method != User.LOGIN_NAVER:
            raise ValidationError(f"{user.login_method}로 로그인 해주세요")
    else:
        if User.objects.filter(nickname=data["nickname"]).exists():
            rand_num = random.randint(0, 99999)
            basenickname = data["nickname"]
            nickname = f"{basenickname}{rand_num}"
        else:
            nickname = data["nickname"]
        user = User(
            email=data["email"],
            nickname=nickname,
            profileImg=data["profileImg"],
            gender=data["gender"],
            name=data["name"],
            login_method=User.LOGIN_NAVER,
        )
        user.set_unusable_password()
        user.save()

    token = TokenObtainPairSerializer.get_token(user)
    refresh_token = str(token)
    access_token = str(token.access_token)

    res = Response(
        {
            "user": serializers.ListUserSerializer(user).data,
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
    return res
