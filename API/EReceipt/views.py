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
from google.cloud import vision

# Models
from .models import Receipt, VerifyCodes

# Serializers
from .serializers import *

# Database
import datetime
from dateutil.relativedelta import relativedelta


# -----------------------------------------------------------
# 회원관리
# 회원가입
class SignupAPI(generics.GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        if len(request.data["password"]) < 4:
            body = {"message": "비밀번호 길이가 너무 짧습니다."}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        try:
            if User.objects.get(email=request.data['email']):
                return Response('이미 등록된 이메일입니다.', status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            pass
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
                "countreceipt": Receipt.objects.all().last().id,
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

        # 가장 최신의 인증코드가 있는 테이블
        query = VerifyCodes.objects.all()
        last_verifycode = query.filter(email=request.data['email']).last()

        if serializer.is_valid():
            if last_verifycode.verify_code == request.data['verify_code']:
                last_verifycode.delete()
                return Response(
                    {
                        "password": User.objects.get(email=request.data['email']).last_name
                    }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------
# 영수증 관리
# 영수증 튜플 생성
class CreateReceiptTuple(generics.GenericAPIView):
    serializer_class = CreateReceiptTupleSerializer

    def post(self, request, *args, **kwargs):
        serializer = CreateReceiptTupleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return_url = 'http://dsc-ereceipt.appspot.com/api/main/check_user_link/{}'.format(
                Receipt.objects.get(receipt_img_url=request.data['receipt_img_url']).id
            )
            return Response(return_url, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 발급된 영수증의 user가 누구인지 확인하고, 영수증 이미지의 링크 url을 반환
class CheckUser(generics.GenericAPIView):
    serializer_class = CheckUserSerializer

    def put(self, request, creat_receipt_id, *args, **kwargs):
        input_data = {"user": self.get_user_id(request.data["username"]),
                      "total_amount": get_total_amount(Receipt.objects.get(id=creat_receipt_id).receipt_img_uri)}

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


# device 코드가 있는 고정 QR코드에 접속했을때 실행
class CheckUserWithDeviceId(generics.GenericAPIView):
    serializer_class = CheckUserSerializer

    def put(self, request, req_device_id):
        request_username = request.data['username']     # 요청한 user의 username
        request_userid = self.get_user_id(request_username)     # 요청한 user의 id
        input_data = {"user": request_userid}

        query = Receipt.objects.all()
        receipt = query.filter(device_id=req_device_id, user=1).last()

        serializer = CheckUserSerializer(receipt, data=input_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_user_id(self, username):
        user_id = User.objects.get(username=username).id
        return user_id


# 영수증 삭제
class DeleteReceipt(generics.DestroyAPIView):
    def delete(self, request, target_id, *args, **kwargs):
        target = Receipt.objects.get(id=target_id)
        try:
            target.delete()
            return Response('Success', status=status.HTTP_202_ACCEPTED)
        except Exception as ex:
            return Response('Error :', ex, status=status.HTTP_400_BAD_REQUEST)


# 영수증에 적힌 총 금액을 받는 함수
def get_total_amount(uri, target_str='Total'):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    txt = []
    target_y = False
    for text in texts:
        txt.append(text.description)
        txt.append(text.bounding_poly.vertices[0].y)
        if text.description == target_str:
            target_y = text.bounding_poly.vertices[0].y

        if target_y and txt[-1] > target_y:
            break

    result = int(txt[-4])
    return result


# -----------------------------------------------------------
# 영수증 리스트 반환
# 사용자 영수증 전체 목록 가져오기
class ReturnReceiptImgList(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer
    queryset = Receipt.objects.all()

    def get(self, request, req_username, *args, **kwargs):
        try:
            user = self.queryset.filter(user=User.objects.get(username=req_username))
            serializer = ReceiptDateSerializer(user, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(ex, status=status.HTTP_400_BAD_REQUEST)


# 선택한 날짜 사이의 영수증 이미지
class ReceiptDateSelect(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer
    queryset = Receipt.objects.all()

    def get(self, request, req_username, s_date, e_date, *args, **kwargs):
        try:
            userquery = self.queryset.filter(user=User.objects.get(username=req_username))
            st_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
            en_date = datetime.datetime.strptime(e_date, '%Y-%m-%d')
            date_format = "%Y-%m-%d"
            start_date = st_date.strftime(date_format)
            end_date = (en_date + datetime.timedelta(days=1)).strftime(date_format)
            queryset = userquery.filter(receipt_date__range=[start_date, end_date])
            serializer = ReceiptDateSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(ex, status=status.HTTP_400_BAD_REQUEST)


# 월별 영수증 이미지
class ReceiptDate(generics.GenericAPIView):
    serializer_class = ReceiptDateSerializer
    queryset = Receipt.objects.all()
    def get(self, request, req_username, month, *args, **kwargs):
        try:
            userquery = self.queryset.filter(user=User.objects.get(username=req_username))
            date_format = "%Y-%m-%d"
            months_ago = (datetime.datetime.now() - relativedelta(months=month)).strftime(date_format)
            now_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
            queryset = userquery.filter(receipt_date__range=[months_ago, now_date])
            serializer = ReceiptDateSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(ex, status=status.HTTP_400_BAD_REQUEST)


# 테스트용
class TestView(APIView):
    serializer_class = TestSerializer()

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = TestSerializer(users, many=True)
        return Response(serializer.data)