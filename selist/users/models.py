from django.contrib.auth.models import AbstractUser
from django.db import models


class Seliste(AbstractUser):
    value = models.IntegerField(default=0)
