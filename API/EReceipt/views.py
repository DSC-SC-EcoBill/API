from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from rest_framework import mixins
from rest_framework import generics
# Models
from .models import Receipt, Qrcodes, ImageCache

# Serializers
from .serializers import SignupSerializer, SigninSerializer, CreateReceiptSerializer, QrUrlSerializer, \
    UserSerializer, NewReceiptURLSerializer, ReceiptListSerializer, ReceiptDateSerializer, NewQrcodesSerializer, \
    ImageCacheSerializer


@api_view(['GET'])
def HelloAPI(request):
    return Response('hello world!')


# 회원가입
class SignupAPI(generics.GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        if len(request.data["password"]) < 4:
            body = {"message": "비밀번호 길이가 너무 짧습니다."}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


# 로그인
class LoginAPI(generics.GenericAPIView):
    serializer_class = SigninSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# 로그인
@api_view(['POST'])
def SignIn(request):
    return Response('Sign in')


# 이미지 추가 및 확인 링크 반환
@api_view(['POST'])
def Upload_Receipt(request):
    return Response('daum.net')


# QR리딩 후 영수증 이미지 반환
@api_view(['GET'])
def ReturnImg(request):
    return Response('Return Img after QR Reading')


# 목록 반환
@api_view(['GET'])
def ReturnList(request, user):
    # now_person = Receipt.objects.get(user=user)
    # serializer = GetListSerializer(now_person)
    return Response('id : {}, Return List'.format(user))


# 선택한 목록의 영수증 이미지 반환
@api_view(['GET'])
def ReturnItemImg(request):
    return Response('Return Img when request Item')


class NewQrcodes(generics.GenericAPIView):
    serializer_class = NewQrcodesSerializer


# 영수증 전체 목록 가져오기
class ReturnReceiptImgList(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           generics.GenericAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 디바이스에서 받아온 영수증 투플생성
class NewReceiptURL(generics.GenericAPIView):
    serializer_class = NewReceiptURLSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save()
        return Response(
            {
                "receipt": NewReceiptURLSerializer(
                    receipt, context=self.get_serializer_context()
                ).data
            }
        )


# 서버로 보내기전 잠시 저장할 영수증이미지 생성
class ImageCache(generics.GenericAPIView):
    serializer_class = ImageCacheSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save()


# 선택한 날짜와 시간의 맞는 영수증 이미지
class ReceiptDate(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer

