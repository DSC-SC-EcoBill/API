from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/signup/', SignupAPI.as_view()),
    path('auth/signin/', SigninAPI.as_view()),

    path('main/searchpw/', SearchPW.as_view()),

    # 디바이스 to API, 영수증 이미지 올리는 url
    path('main/upload_img/', UploadIMG.as_view()),
    path('main/check_user_link/<int:creat_receipt_id>', CheckUser.as_view()),

    path('main/return_receipt_img_List/', ReturnReceiptImgList.as_view()),
    path('main/receipt_url/', NewReceiptURL.as_view()),

    path('main/receipt_date/', ReceiptDate.as_view()),
    path('main/receipt_date_select/', ReceiptDateSelect.as_view()),
]

