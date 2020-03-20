from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from rest_framework import mixins
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend


# Google cloud platform
from google.cloud import storage


# Models
from .models import Receipt, Qrcodes, ImageCache

# Serializers
from .serializers import *


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
class SigninAPI(generics.GenericAPIView):
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


# 로그인 확인
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


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


# 사용자 영수증 전체 목록 가져오기
class ReturnReceiptImgList(generics.ListAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptDateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']


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
class UploadIMG(generics.GenericAPIView):
    serializer_class = ImageCacheSerializer  # 이미지를 스토리지로 넘기기전에 잠시 저장해두는 시리얼라이저

    def post(self, request, *args, **kwargs):
        # request로 올라온 이미지를 임시저장 테이블에 저장
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            img_data = serializer.save()

        # DB의 이미지 데이터 가져오기
        cache_img = ImageCache.objects.get(id=img_data.id, device_id=img_data.device_id)    # 업로드할 튜플
        file_name = cache_img.image                                                         # 업로드할 이미지의 파일 객체
        blob_name = 'receipts/{}.jpg'.format(cache_img.image_name)                          # 업로드할 이미지의 gcs 경로

        # gcs에 이미지 업로드 요청
        try:
            self.upload_file_gcs(file_name, blob_name)
        except Exception as ex:
            print('Hey! : ', ex)

        # gcs에 저장된 이미지의 link url 반환 요청
        try:
            link_url = self.get_linkurl_gcs(blob_name)
        except Exception as ex:
            print('Hey!: ', ex)

        # 받은 link url을 이용해 Receipt Tuple 생성
        dummy_user = User(id=1)
        new_receipt = Receipt(
            receipt_img_url=link_url,
            device_id=img_data.device_id,
            user=dummy_user
        )
        new_receipt.save()

        # 사용자를 확인할 수 있는 임의의 url 생성 후 반환
        check_user_link = 'http://127.0.0.1:8000/api/main/check_user_link/{}'.format(new_receipt.id)
        return Response(check_user_link)

    # 스토리지 파일 업로드 함수
    def upload_file_gcs(self, file_name, destination_blob_name, bucket_name='dsc_ereceipt_storage'):
        # file_name : 업로드할 파일명
        # destination_blob_name : 업로드될 경로와 파일명
        # bucket_name : 업로드할 버킷명
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_file(file_name)

        print(
            "File {} uploaded to {}".format(
                file_name, destination_blob_name
            )
        )

    # 스토리지에 업로드된 파일의 링크url을 가져오는 함수
    def get_linkurl_gcs(self, blob_name, bucket_name='dsc_ereceipt_storage'):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        print(
            "Blob {}'s url : {}".format(
                blob_name, blob.public_url
            )
        )

        return blob.public_url


# 발급된 영수증의 user가 누구인지 확인하고, 영수증 이미지의 링크 url을 반환
# 저장을 눌렀는지, 아닌지에 따라서 is_Storage 값을 변경
class CheckUser(generics.GenericAPIView):
    serializer_class = CheckUserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            my_receipt = Receipt.objects.get(id=request.data['id'])             # 영수증 튜플
            my_receipt.user_id = self.get_user_id(request.data['username'])

            my_receipt.save()   # Tuple Update

        return Response(my_receipt.receipt_img_url)

    # 사용자의 고유 id를 반환하는 함수
    def get_user_id(self, username):
        user_id = User.objects.get(username=username).id
        print(user_id)
        return user_id


# 선택한 날짜와 시간의 맞는 영수증 이미지
class ReceiptDate(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer

