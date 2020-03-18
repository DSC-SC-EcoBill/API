from abc import ABC

from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Devices, Receipt, Qrcodes, File


# 회원가입
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"], first_name=validated_data["first_name"],
            email=validated_data["email"]
        )
        return user


# 접속 유지중인가 확인
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


# 로그인
class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


# 생성된 행의 사용자를 확인
class CreateReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('receipt_img_url', 'receipt_img_')


# QR코드로 변환될 확인 url
class QrUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('id', 'qr_url')


# 목록 가져오기
class GetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('id', 'receipt_date', 'user')


# 선택한 날짜와 시간의 맞는 영수증 이미지
class GetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('receipt_img_url', 'user')


# 영수증 이미지를 잠시 저장하는 시리얼라이저
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
