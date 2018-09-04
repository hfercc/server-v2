# -*- coding: utf-8 -*-
from rest_framework import serializers, status
from .models import Report
from rest_framework.validators import UniqueValidator
from django.db.models import Q
class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class ReportsCreateSerializer(serializers.ModelSerializer):
    alpha_name = serializers.CharField(required=True, allow_blank=False)
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    error_message = serializers.ReadOnlyField()
    backtest_img = serializers.ReadOnlyField()
    def validate(self, data):
        alpha_name = data['alpha_name']
        user = self.context['request'].user
        queryset = Report.objects.filter(Q(author__exact=user) & Q(alpha_name__exact=alpha_name))
        print(user, alpha_name, queryset)
        if len(queryset) > 0:
            raise serializers.ValidationError(u'因子重名！', code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return data
    class Meta:
        model = Report
        fields = '__all__'