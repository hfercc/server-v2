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
    self.types = ['longshort','longonly','IC_hedge','IF_hedge']
    self.universe = ['ALL','zz500','hs300']
    def validate(self, data):
        alpha_name = '_'.join(['alpha',data['alpha_name'], self.types[data['types']], self.universe[data['universe']]])
        user = self.context['request'].user
        queryset = Report.objects.filter(Q(author__exact=user) & Q(alpha_name__exact=alpha_name))
        data['alpha_name'] = alpha_name
        if len(queryset) > 0:
            raise serializers.ValidationError(u'因子重名！', code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return data
    class Meta:
        model = Report
        fields = '__all__'

class ReportsReuploadSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('file',)
        model = Report