from django.db import models
from django.contrib.auth.models import User

class Satellite(models.Model):
    satellite_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)
    image_url = models.URLField()
    weight = models.CharField(max_length=50)
    orbit = models.CharField(max_length=255)
    expected_date = models.DateField()

    class Meta:
        managed = False
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
    creator = models.ForeignKey(User,null=True, on_delete=models.PROTECT)
    rocket = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_launches')

    class Meta:
        managed = False
        db_table = 'launches'

class LaunchSatellite(models.Model):
    launch = models.ForeignKey(Launch, on_delete=models.CASCADE)
    satellite = models.ForeignKey(Satellite, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        managed = False
        db_table = ('launch_satellite')
        unique_together = (('launch_id', 'satellite_id'),)
