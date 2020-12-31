from django_rest_passwordreset.signals import reset_password_token_created
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail

from django.urls import reverse
from django.utils.text import slugify

import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from django.db import IntegrityError
from django.db import transaction

from django.conf import settings
from jumga.extras import CharNullField


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset()\
            .filter(is_active=True)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=128, unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()
    active_now = ActiveManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Merchant(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='merchant')
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    phone_number = CharNullField(
        max_length=18, unique=True, blank=True, null=True, default=None)

    class Meta:
        db_table = 'merchant'

    def __str__(self):
        return self.user.email

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class Customer(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer')

    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    phone_number = CharNullField(
        max_length=18, unique=True, blank=True, null=True, default=None)

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return self.user.email

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class Rider(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='rider')

    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    phone_number = CharNullField(
        max_length=18, unique=True, blank=True, null=True, default=None)

    class Meta:
        db_table = 'rider'

    def __str__(self):
        return self.user.email

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

# SIGNALS


def set_username(sender, instance, **kwargs):
    if not instance.username:
        instance.username = "user_"+str(uuid.uuid4())[:8]


models.signals.pre_save.connect(set_username, sender=User)
