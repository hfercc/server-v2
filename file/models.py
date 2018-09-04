from django.db import models
from django.contrib.auth import get_user_model
from report.models import Report
User = get_user_model()
# Create your models here.
class FileRecord(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    file_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    path = models.CharField(max_length=100)