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
from .models import Receipt, Qrcodes, VerifyCodes

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
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 사용자 영수증 전체 목록 가져오기
class ReturnReceiptImgList(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer

    # def get_queryset(self):
    #     query = Receipt.objects.all()
    #     user = self.request.query_params.get('user', None)
    #     if user is not None:
    #         queryset = query.filter(user=user)
    #     return queryset

    def get(self, request, req_username, *args, **kwargs):
        query = Receipt.objects.all()
        user = query.filter(user=User.objects.get(username=req_username))
        serializer = ReceiptDateSerializer(user)    # 여기가 오류나는 부분;;;; 값 하나만 보내는건 되는데 리스트로는 불가능한거 같아
        return Response(req_username)


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


# 영수증 튜플 생성
class CreateReceiptTuple(generics.GenericAPIView):
    serializer_class = CreateReceiptTupleSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateReceiptTupleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            receipt_id = Receipt.objects.get(receipt_img_url=request.data['receipt_img_url']).id
            return_url = 'http://dsc-ereceipt.appspot.com/api/main/check_user_link/{}'.format(receipt_id)
            return Response(return_url, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 발급된 영수증의 user가 누구인지 확인하고, 영수증 이미지의 링크 url을 반환(확정)
class CheckUser(generics.GenericAPIView):
    serializer_class = CheckUserSerializer

    def put(self, request, creat_receipt_id, *args, **kwargs):
        input_data = {"user": self.get_user_id(request.data["username"])}

        receipt = Receipt.objects.get(id=creat_receipt_id)
        serializer = CheckUserSerializer(receipt, data=input_data)

        if serializer.is_valid():
            serializer.save()
            linkurl = receipt.receipt_img_url
            return Response(linkurl)
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


class TestView(APIView):
    serializer_class = TestSerializer()

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = TestSerializer(users, many=True)
        return Response(serializer.data)
