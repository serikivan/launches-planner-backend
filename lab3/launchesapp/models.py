from django.db import models
from django.contrib.auth import get_user_model

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        managed = False
        db_table = 'auth_user'

class Satellite(models.Model):
    satellite_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    image_url = models.URLField(null=True)
    weight = models.CharField(max_length=50)
    orbit = models.CharField(max_length=255)
    expected_date = models.DateField()
    user = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, blank=False,
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
    creator = models.ForeignKey(AuthUser,null=True, blank=True, related_name='launch_creator', on_delete=models.DO_NOTHING)
    rocket = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    success = models.BooleanField(null=True)
    moderator = models.ForeignKey(AuthUser,null=True, blank=True, related_name='launch_mod', on_delete=models.DO_NOTHING)

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