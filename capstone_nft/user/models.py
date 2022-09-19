from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .mixin import TimedModelMixin
from .user_manager import UserManager


class User(AbstractUser, TimedModelMixin):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    name = models.CharField(max_length=64, default='', null=True, blank=True, verbose_name='이름')
    nick_name = models.CharField(max_length=64, unique=True, verbose_name='닉네임')
    phoneNumberRegex = RegexValidator(regex=r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$')
    phone = models.CharField(validators=[phoneNumberRegex], max_length=11, unique=True, verbose_name='전화 번호')
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')

    @property
    def following_num(self):
        return self.followings.count()
    
    @property
    def follower_num(self):
        return self.followers.count()

    def get_username(self):
        return self.email

    class Meta:
        verbose_name = "사용자 정보"
        verbose_name_plural = "사용자 정보들"

