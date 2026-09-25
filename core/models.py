from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, first_name, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required.")
        
        user = self.model(phone=phone, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, first_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        
        if hasattr(self.model, 'is_staff'):
            extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_superuser=True.')

        return self.create_user(phone, first_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, verbose_name="Phone", unique=True)
    first_name = models.CharField(max_length=200, verbose_name="First name")
    email = models.EmailField(verbose_name="Email", unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False) 

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return f'{self.first_name} - phone : {self.phone}'