from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
import uuid


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        db_table = "user"

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=30)
    password = models.CharField(
        max_length=128,
        validators=[
            RegexValidator(
                regex="(?=.*\d)(?=.*[a-z])(?=.*\W)[a-zA-Z\d\W]{8,}$",
                message="비밀번호에 특수문자, 숫자, 영문자를 포함하여 8자리 이상이어야 합니다.",
                code="invalid_password",
            )
        ],
    )
    last_login = models.DateTimeField(blank=True, null=True)
    login_count = models.IntegerField(default=0)
    banned_at = models.DateTimeField(blank=True, null=True)
    is_dormant = models.BooleanField(default=False)
    is_withdraw = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    withdraw_at = models.DateTimeField(blank=True, null=True)
    change_password_at = models.DateTimeField(blank=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Verify(models.Model):
    class Meata:
        db_table = "verify"

    email = models.EmailField()
    code = models.CharField(max_length=6)
    is_verify = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=24)
    profileimage = models.ImageField(upload_to="profile_img/", null=True, blank=True)
    introduction = models.TextField(null=True, blank=True, default=None)
    region = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.nickname)


class GuestBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comment_set"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)

class PasswordReset(models.Model):
    class Meta:
        db_table = "password_reset"

    email = models.EmailField()
    uuid = models.CharField(max_length=255)
    is_verify = models.BooleanField(default=False)

