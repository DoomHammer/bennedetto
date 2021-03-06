from uuid import uuid4
import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from timezone_field import TimeZoneField
from django.utils import timezone
import pytz


def get_default_timezone():
    return pytz.timezone('US/Central')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.model(email=email)
        user.set_password(password)
        user.is_staff = True
        user.save()
        return user

    def midnight(self, now=None):
        '''
        returns all users that are *currently* experiencing
        the first hour of their day
        '''
        now = now or datetime.now(pytz.utc)
        zones = [tz for tz in pytz.common_timezones_set
                 if now.astimezone(pytz.timezone(tz)).hour == 0]
        return self.filter(timezone__in=zones)


class User(AbstractBaseUser):
    objects = UserManager()

    id = models.UUIDField(primary_key=True,
                          unique=True,
                          editable=False,
                          default=uuid4)

    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    timezone = TimeZoneField(default=get_default_timezone)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.get_short_name()

    def get_short_name(self):
        return self.email

    def has_perm(self, *args, **kwargs):
        return self.is_staff

    def has_module_perms(self, *args):
        return self.is_staff

    def activate_timezone(self):
        timezone.activate(self.timezone)
