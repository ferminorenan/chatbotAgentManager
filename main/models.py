from django.contrib.auth.models import User
from django.db import models
import secrets

class Project(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    users = models.ManyToManyField(User, related_name='projects')
    is_active = models.BooleanField(default=True)
    token = models.CharField(max_length=100, default=secrets.token_hex)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name