from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken

# Models
from .models import Guests, Devices, Receipt, Qrcodes

# Serializers
from .serializers import SignupSerializer, SigninSerializer, CreateReceiptSerializer, \
    QrUrlSerializer, GetListSerializer, GetItemSerializer


@api_view(['GET'])
def HelloAPI(request):
    return Response('hello world!')


# 회원가입
@api_view(['POST'])
def SignUp(request):
    return Response('Sign up')


# 로그인
@api_view(['POST'])
def SignIn(request):
    return Response('Sign in')


# 이미지 추가 및 확인 링크 반환
@api_view(['POST'])
def MakeQR(request):
    return Response('Make QR')


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

