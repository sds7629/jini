import asyncio
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from asgiref.sync import sync_to_async, async_to_sync
from adrf.decorators import api_view
from . import serializers


User = get_user_model()

asend_mail = sync_to_async(send_mail, thread_sensitive=False)


async def send_email(subject, message, mail_to) -> None:
    asyncio.create_task(
        await asend_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[mail_to],
        )
    )


@api_view(["PUT"])
async def reset_password_sendmail(request):
    try:
        serializer = serializers.PasswordChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.get(email=email)
        current_site = get_current_site(request)
        message = render_to_string(
            "users/reset_password.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": email_activation_token.make_token(user),
            },
        )
        mail_title = "비밀번호 재설정 메일"
        mail_to = request.data.get("email")
        asyncio.create_task(send_email(mail_title, message, mail_to))
        return Response(
            "인증 메일이 발송되었습니다.",
            status=status.HTTP_200_OK,
        )

    except (ValueError, OverflowError, User.DoesNotExist):
        return Response(
            "해당 이메일로 가입된 사용자가 존재하지 않습니다.",
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmailVerificationToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


email_activation_token = EmailVerificationToken()


def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and email_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        res = redirect("http://locahost:3000")
        res.set_cookie("accesstoken", access_token, httponly=True)
        res.set_cookie("refresh_token", refresh_token, httponly=True)
        return res
