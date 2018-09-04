from rest_framework import serializers
from .models import FileRecord
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileRecord
        fields = '__all__'

