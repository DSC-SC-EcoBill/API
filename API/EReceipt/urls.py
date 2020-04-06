from django.urls import path
from .views import *

urlpatterns = [
    path('auth/signup/', SignupAPI.as_view()),                                  # 회원가입
    path('auth/signin/', SigninAPI.as_view()),                                  # 로그인

    path('main/searchpw/', SearchPW.as_view()),                                 # 비밀번호 찾기
    path('main/searchpwcode/', SearchPWCode.as_view()),                         # 비밀번호 찾기 with 인증코드

    # 디바이스 to API, 영수증 튜플 생성
    path('main/upload_img/', CreateReceiptTuple.as_view()),                     # 영수증 튜플 생성


    path('main/check_user_link/<int:creat_receipt_id>', CheckUser.as_view()),   # 유저확인하기

    path('main/receipt_url/', NewReceiptURL.as_view()),

    # 영수증 리스트 반환
    path('main/return_receipt_img_List/', ReturnReceiptImgList.as_view()),      # 전체 반환
    path('main/receipt_date/', ReceiptDate.as_view()),                          # 개월 단위로 반환
    path('main/receipt_date_select/', ReceiptDateSelect.as_view()),             # 지정한 날짜 단위로 반환
]

