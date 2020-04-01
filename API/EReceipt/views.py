from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken
from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend

# Gmail 발송
import smtplib
from email.mime.text import MIMEText

# 난수 생성
import random

# Google cloud platform
from google.cloud import storage

# Models
from .models import Receipt, Qrcodes, ImageCache, VerifyCodes

# Serializers
from .serializers import *

# Database
import datetime
from dateutil.relativedelta import relativedelta


# 회원가입(확정)
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


# 로그인(확정)
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


# 비밀번호 찾기
class SearchPW(generics.GenericAPIView):
    serializer_class = SearchPWSerializer

    def post(self, request, *args, **kwargs):
        input_data = {'email': request.data['email'], 'verify_code': self.verify_code_generator()}
        serializer = SearchPWSerializer(data=input_data)

        if serializer.is_valid():
            # verify_code 테이블에 tuple 생성

            serializer.save()

            # 이메일 작성
            first_name = User.objects.get(email=request.data['email']).first_name
            subject = 'Did you ask your password from Ereceipt app?'
            body = '''
            Hello {}!!
            We are Ereceipt team.
            We send your verify code for search password.
            If you doesn't request search password, please contact to us :)

            This is your verify code
            {}

            Please write the code in your application.

            -------------------------
            Thanks to use our Ereceipt service!
            '''.format(first_name, input_data['verify_code'])
            self.send_email(request.data['email'], subject, body)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    # Gmail을 보내는 함수
    def send_email(self, email, subject, body):
        try:
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login('dev.ksanbal@gmail.com', 'jkybizzwutfgwstn')

            msg = MIMEText(body)
            msg['Subject'] = subject
            session.sendmail('Ereceipt@gmail.com', email, msg.as_string())
            print('successfully send email')

        except Exception as ex:
            print("Hey! ", ex)

    # 인증코드 생성기
    def verify_code_generator(self):
        random_code = []

        # 5자리 난수 생성
        for _ in range(5):
            random_code.append(str(random.randint(0, 9)))

        verify_code = ''.join(random_code)
        print(verify_code)

        return verify_code


# 비밀번호 찾기 with 인증코드
class SearchPWCode(generics.GenericAPIView):
    serializer_class = SearchPWSerializer

    def post(self, request, *args, **kwargs):
        serializer = SearchPWSerializer(data=request.data)

        if VerifyCodes.objects.get(email=request.data['email']).verify_code == request.data['verify_code']:
            VerifyCodes.objects.get(email=request.data['email']).delete()
            return Response(
                {
                    "password": User.objects.get(email=request.data['email']).last_name
                }
            )
        else:
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 사용자 영수증 전체 목록 가져오기
class ReturnReceiptImgList(generics.ListAPIView):
    serializer_class = ReceiptDateSerializer

    def get_queryset(self):
        query = Receipt.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = query.filter(user=user)
        return queryset


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


# 서버로 보내기전 잠시 저장할 영수증이미지 생성(확정)
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


# 발급된 영수증의 user가 누구인지 확인하고, 영수증 이미지의 링크 url을 반환(확정)
# 저장을 눌렀는지, 아닌지에 따라서 is_Storage 값을 변경
class CheckUser(generics.GenericAPIView):
    serializer_class = CheckUserSerializer

    def put(self, request, creat_receipt_id, *args, **kwargs):
        input_data = {"user": self.get_user_id(request.data["username"])}

        receipt = Receipt.objects.get(id=creat_receipt_id)
        serializer = CheckUserSerializer(receipt, data=input_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 사용자의 고유 id를 반환하는 함수
    def get_user_id(self, username):
        user_id = User.objects.get(username=username).id
        return user_id


# 선택한 날짜 사이의 영수증 이미지
class ReceiptDateSelect(generics.ListAPIView):
    serializer_class = ReceiptDateSerializer

    def get_queryset(self, *args, **kwargs):
        user = self.request.data['user']
        s_date = self.request.data['s_date']
        st_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
        e_date = self.request.data['e_date']
        en_date = datetime.datetime.strptime(e_date, '%Y-%m-%d')
        date_format = "%Y-%m-%d"
        start_date = st_date.strftime(date_format)
        end_date = (en_date + datetime.timedelta(days=1)).strftime(date_format)
        queryset = Receipt.objects.filter(receipt_date__range=[start_date, end_date], user=user)
        return queryset


# 월별 영수증 이미지
class ReceiptDate(generics.ListAPIView):
    serializer_class = ReceiptDateSerializer

    def get_queryset(self, *args, **kwargs):
        user = self.request.data['user']
        months = self.request.data['months']
        date_format = "%Y-%m-%d"
        if months == "1":
            months_ago = (datetime.datetime.now() - relativedelta(months=1)).strftime(date_format)
            now_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
            queryset = Receipt.objects.filter(receipt_date__range=[months_ago, now_date], user=user)
            return queryset

        elif months == "3":
            months_ago = (datetime.datetime.now() - relativedelta(months=3)).strftime(date_format)
            now_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
            queryset = Receipt.objects.filter(receipt_date__range=[months_ago, now_date], user=user)
            return queryset

        elif months == "6":
            months_ago = (datetime.datetime.now() - relativedelta(months=6)).strftime(date_format)
            now_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
            queryset = Receipt.objects.filter(receipt_date__range=[months_ago, now_date], user=user)
            return queryset