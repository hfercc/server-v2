# users.views.py

from django.contrib.auth.backends import ModelBackend
from rest_framework import decorators

from django.db.models import Q
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from rest_framework import permissions, viewsets, status, decorators
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response

from random import choice
from .serializer import UserRegSerializer, UserDetailSerializer, ChangePasswordSerializer
from django.contrib.auth import login as auth_login, logout as auth_logout
from .mixins import BaseUserViewSetMixin
from django.contrib.auth import get_user_model
from datetime import datetime
from rest_framework_jwt.views import JSONWebTokenAPIView, api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from utils.utils import store_file
User = get_user_model()
def jwt_response_payload_handler(token, user, request):
    return {
        'token': token, 
        'user': UserDetailSerializer(user, context={'request': request}).data
    }

class BasicLoginView(JSONWebTokenAPIView):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expirationm, httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserLogin(BasicLoginView):
    serializer_class = JSONWebTokenSerializer

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def change_password(request):

    serializer = ChangePasswordSerializer(
        data=request.data, context=dict(request=request))

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response('OK')

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):

    if 'file' not in request.FILES:
        raise ValidationError('Field `file` not found.')

    filename, _ = store_file(request.FILES['file'])
    url = default_storage.url(filename)

    request.user.update_avatar(url)

    return Response(url)
re_user_lookup_value = r'\d+|me'
class UserViewset(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, BaseUserViewSetMixin):
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    lookup_value_regex = re_user_lookup_value
    lookup_url_kwarg = 'user_pk'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["user"] = user
        headers = self.get_success_headers(serializer.data)

        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        return []
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer
    def get_object(self):
        obj = self.get_user_object()
        #self.check_object_permissions(self.request, obj)
        return obj
