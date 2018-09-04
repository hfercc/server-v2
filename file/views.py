from django.shortcuts import render
from django.http import FileResponse, Http404

from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsOwnerOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from rest_framework import mixins
from rest_framework import generics, permissions
from rest_framework import decorators
from django.db.models import Q
from rest_framework.response import Response

from .models import FileRecord

from .serializer import FileSerializer

# Create your views here.
@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def download_key(request, report, file_name):
    user = request.user  
    if file_name:
        files = FileRecord.objects.filter(Q(author=user) & Q(report__alpha_name=report) & Q(name=file_name))
        if len(files) > 0:
            ret = FileResponse(open(files[0].path, 'rb'))
            filename = files[0].path.split('/')[-1]
            ret['Content-Type']='application/octet-stream' 
            ret['Content-Disposition'] = 'attachment; filename="%s"' % filename
            return ret
        else:
            raise Http404("File Not Found")
    else:
        serializer = FileSerializer(FileRecord.objects.filter(Q(author=user) & Q(report__alpha_name=report)), many=True)
        return Response(serializer.data)
