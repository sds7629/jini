from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True  # 마이그레이션에 UserManager에 포함하는 코드

    def create_user(
        self,
        email,
        nickname,
        profileImg,
        gender,
        name,
        password=None,
        **kwargs,
    ):
        if not email:
            raise ValueError("이메일은 필수사항입니다.")
        user = self.model(
            email=email,
            nickname=nickname,
            profileImg=profileImg,
            gender=gender,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)  # 기본 User 모델을 이용하여 저장하는 코드
        return user

    def create_superuser(
        self,
        email,
        nickname,
        gender,
        name,
        profileImg=None,
        password=None,
        **extra_fields,
    ):
        user = self.create_user(
            email=email,
            password=password,
            nickname=nickname,
            profileImg=profileImg,
            gender=gender,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    class GenderChoices(models.TextChoices):
        """
        성별 선택 모델 index[1]의 내용이 보여지는 값 index[0]의 내용이 실제 db에 저장되는 값
        """

        MALE = ("male", "Male")
        FEMALE = ("female", "Female")

    email=models.EmailField(verbose_name="email address", max_length= 100, unique=True, null=False, blank=False) 
    gender = models.CharField(max_length=6, choices=GenderChoices.choices)
    nickname = models.CharField(max_length=15, unique=True, null=False, blank=False)
    name = models.CharField(max_length=10)
    profileImg = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"  # 로그인에 사용되는 필드입니당
    REQUIRED_FIELDS = ["nickname", "name", "gender"] #어드민유저 만들때

    def __str__(self):
        return self.email

    def is_staff(self):
        return self.is_superuser

    class Meta:
        db_table = "user"