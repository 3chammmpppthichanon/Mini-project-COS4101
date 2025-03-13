from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, role, password=None):
        if not email:
            raise ValueError('The email address is required')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        user.set_password(password)  # hash รหัสผ่านก่อนที่จะบันทึกลงฐานข้อมูล
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, role, password):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role='Admin',
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Advisor', 'Advisor'),
        ('Admin', 'Admin')
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active =
