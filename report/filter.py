import django_filters
from .models import Report

class ReportsFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model=Report
        fields=['name']