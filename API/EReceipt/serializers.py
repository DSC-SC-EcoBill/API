from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Receipt, Qrcodes, ImageCache, VerifyCodes


# 회원가입(확정)
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"]
        )
        return user


# 접속 유지중인가 확인(확정)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


# 로그인(확정)
class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


# 비밀번호 찾기
class SearchPWSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', )


# 서버로 보내기전 잠시 저장할 영수증이미지 생성 (확정)
class ImageCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCache
        fields = ('id', 'upload_data', 'device_id', 'image_name', 'image')

        def create(self, validated_data):
            image = ImageCache.objects.create(
                upload_data=validated_data["upload_data"],
                image=validated_data["image"]
            )
            return image


# 생성된 영수증 tuple에 사용자를 추가하는 시리얼라이저(확정)
class CheckUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('user',)

    # def update(self, instance, validated_data):
    #     instance.user_id = validated_data.get('user_id', instance.user_id)
    #     instance.save()
    #     return instance


# 서버에서 받아온 영수증주소 투플생성
class NewReceiptURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('id', 'user', 'receipt_img_url', 'device_id')

    def create(self, validated_data):
        receipt = Receipt.objects.create(
            user=validated_data["user"], receipt_img_url=validated_data["receipt_img_url"],
            device_id=validated_data["device_id"]
        )
        return receipt


# 영수증 투플삭제
# class DeleteReceiptSerializer(serializers.ModelSerializer):


# 영수증 QR코드 투플생성
class NewQrcodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qrcodes
        fields = ('id', 'qr_url', 'receipt')

    def create(self, validated_data):
        qrcodes = Qrcodes.objects.create(
            qr_url=validated_data["qr_url"], receipt=validated_data["receipt"]
        )
        return qrcodes


# 영수증 목록 가져오기
class ReceiptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('id', 'user', 'receipt_img_url', 'receipt_date')


# 선택한 날짜와 시간의 맞는 영수증 이미지리스트
class ReceiptDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ('id', 'user', 'receipt_img_url', 'receipt_date')


# 테스트
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifyCodes
        fields = ('email', 'verify_code')
    #
    # def create(self, validated_data):
    #     test = VerifyCodes.objects.create(
    #         email=validated_data['email'],
    #         verify_code=validated_data['verify_code']
    #     )
    #     return test
