# -*- coding: utf-8 -*-
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
User = get_user_model()
class UserRegSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label=u"用户名", help_text=u"用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message=u"用户已经存在")])
    password = serializers.CharField(
        style={'input_type': 'password'},label=True,write_only=True
    )
    email = serializers.CharField(label=u"邮件地址",write_only=True, allow_blank=True)

    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username','email', 'password')

class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情
    """
    class Meta:
        model = User
        fields = ("username","email", "id")

class ChangePasswordSerializer(serializers.Serializer):

    old = serializers.CharField(required=True)
    new = serializers.CharField(required=True)
    def validate_old(self, value):
        username = self.context['request'].user.username
        if authenticate(username=username, password=value) is None:
            raise serializers.ValidationError(
                'Old password mismatched!', code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return value

    def validate(self, data):
        new = data['new']
        validate_password(new)

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        user.set_password(validated_data['new'])
        user.save()

        return user
