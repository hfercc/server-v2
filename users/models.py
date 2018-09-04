# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserProfile(AbstractUser):
    avatar = models.TextField()

    def __unicode__(self):
        return self.username