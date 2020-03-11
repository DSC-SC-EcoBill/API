from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Guests, Devices, Receipt, Qrcodes


# 회원가입
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guests
        fields = ('user_id', 'password', 'name', 'jumin_no', 'email')

    def create(self, validated_data):
        return 'create'


# 로그인
class SigninSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guests
        fields = ('user_id', 'password')

    def validate(self, attrs):
        return 'validate'


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
        fields = ('receipt_date', 'user')


# 선택한 날짜와 시간의 맞는 영수증 이미지
class GetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('receipt_img_url', 'user')

