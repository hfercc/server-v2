# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()
class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    file = models.CharField(max_length=100)
    status = models.IntegerField(default=0)#0: default, 1:pending, 2:finished, 3:error
    alpha_name = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=datetime.now)
    error_message = models.CharField(max_length=100, blank=True, default="")
    #modified_time = models.DateTimeField(u"修改时间", default=datetime.now)
    backtest_img = models.CharField(max_length=100, blank=True, default="")