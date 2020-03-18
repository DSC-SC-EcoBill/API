from django.urls import path
from .views import *

urlpatterns = [
    path('auth/signup/', SignupAPI.as_view()),
    path('auth/signin/', SigninAPI.as_view()),

    path('main/gcptest/', Upload_Receipt),

    path('main/return_receipt_img_List/', ReturnReceiptImgList.as_view()),
    path('main/receipt_url/', NewReceiptURL.as_view()),
    path('main/receipt_date/', ReceiptDate.as_view()),
    path('main/imagecache/', ImageCache.as_view()),
]
