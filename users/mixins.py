from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
User = get_user_model()

re_user_lookup_value = r'\d+|me'
class BaseUserViewSetMixin(viewsets.GenericViewSet):
    user_lookup_value_regex = re_user_lookup_value
    def get_user_queryset(self):
        return User.objects.all()
    def get_user_object(self):
        lookup = self.kwargs['user_pk']
        if lookup == 'me':
            if not self.request.user.is_authenticated:
                raise NotFound
            if self.action != 'retrieve':
                return self.request.user
            lookup = str(self.request.user.id)

        return get_object_or_404(self.get_user_queryset(), pk=lookup)
