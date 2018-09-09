from .serializer import ReportsSerializer, ReportsCreateSerializer, ReportsReuploadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import mixins
from rest_framework import generics, permissions
from rest_framework import decorators
from rest_framework.pagination import PageNumberPagination
from .models import Report
from utils.utils import store_file

from rest_framework import viewsets
from rest_framework import filters

from .filter  import ReportsFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsOwnerOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
# Create your views here.


@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def upload_report(request):
    if 'file' not in request.FILES:
        raise ValidationError('Field `file` not found.')

    filename, _ = store_file(request.FILES['file'], request.user, request.data['alpha_name'])
    url = default_storage.url(filename)

    #request.user.update_avatar(url)
    return Response(url)

class ReportsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param="p"
    max_page_size = 1000


class ReportsViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication,SessionAuthentication)
    queryset = Report.objects.all()
    serializer_class = ReportsSerializer
    pagination_class = ReportsPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_class = ReportsFilter
    search_fields = ('alpha_name',)
    ordering_fields = ('report_id', 'alpha_name', 'add_time', 'status')
    ordering = ('-add_time', )
    def get_serializer_class(self):
        if  self.action == "update" or self.action == 'partial_update':
            return ReportsReuploadSerializer
        elif self.action == "create":
            return ReportsCreateSerializer
        else:
            return ReportsSerializer
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(status=0)
        
    def get_queryset(self):
        queryset = Report.objects.filter(author=self.request.user)
        return queryset
    #search_fields = ('name')