from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group, Permission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model

class NewUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=128, verbose_name="Пароль")
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    groups = models.ManyToManyField(Group, related_name='customuser_groups')  # Уникальное related_name
    user_permissions = models.ManyToManyField(Permission,related_name='customuser_permissions')  # Уникальное related_name

    USERNAME_FIELD = 'email'

    objects = NewUserManager()

class Satellite(models.Model):
    satellite_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    image_url = models.URLField(null=True)
    weight = models.CharField(max_length=50)
    orbit = models.CharField(max_length=255)
    expected_date = models.DateField()
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True, blank=False,
                             verbose_name="sat_creator")

    class Meta:
        managed = True
        db_table = 'satellites'

class Launch(models.Model):
    launch_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    creator = models.ForeignKey(CustomUser,null=True, blank=True, related_name='launch_creator', on_delete=models.DO_NOTHING)
    rocket = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    success = models.BooleanField(null=True)
    moderator = models.ForeignKey(CustomUser,null=True, blank=True, related_name='launch_mod', on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'launches'

class LaunchSatellite(models.Model):
    id = models.AutoField(primary_key=True)
    launch = models.ForeignKey(Launch, on_delete=models.CASCADE, related_name='linked_launches')
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE, related_name='linked_satellites')
    order = models.PositiveIntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'launch_satellite'
        unique_together = (('launch_id', 'satellite_id'),)