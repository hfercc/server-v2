from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse

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
import re
import csv

# Create your views here.
@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def download_key(request, report, file_name):
    user = request.user  
    if file_name:
        files = FileRecord.objects.filter(Q(author=user) & Q(report__alpha_name=report) & Q(name=file_name))
        if len(files) > 0:
            if file_name == 'output_pnl.png':
                ret = FileResponse(open(files[0].path, 'rb'))
                filename = files[0].path.split('/')[-1]
                ret['Content-Type'] = 'image/jpeg'
            elif file_name == 'output_performance.csv':
                ret = []
                with open(files[0].path) as f:
                    r = list(csv.reader(f))
                print(r)
                regex = re.compile('\s+')
                columns = regex.split(r[0][0].strip())
                columns[0] = 'period'
                for i in range(1, len(r)):
                    ret.append(zip(columns, regex.split(r[i][0].strip())))
                return HttpResponse(ret)

            else:
                ret = FileResponse(open(files[0].path, 'rb'))
                ret['Content-Type']='application/octet-stream'
            return ret
        else:
            raise Http404("File Not Found")
    else:
        serializer = FileSerializer(FileRecord.objects.filter(Q(author=user) & Q(report__alpha_name=report)), many=True)
        return Response(serializer.data)
