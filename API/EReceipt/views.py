from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from knox.models import AuthToken

# from .serializers import


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
    return Response('Return IMG')


# 목록 반환
@api_view(['GET'])
def ReturnList(request):
    return Response('Return List')

