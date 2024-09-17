from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

#ログイン用モデル
class User(AbstractBaseUser, PermissionsMixin):
    user_vali = UnicodeUsernameValidator()
    username = models.CharField(_('username'), max_length=150, unique=True, validators=[user_vali])
    is_staff = models.BooleanField(_('staff status'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
