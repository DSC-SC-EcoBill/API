from django.urls import path
from .views import *

urlpatterns = [
    path('hello/', HelloAPI),
    path('auth/signup/', SignupAPI.as_view()),
    path('auth/signin/', SignIn),
    path('main/rimg/', ReturnImg),
    path('main/rlist/', ReturnList),
    path('main/ritemimg/', ReturnItemImg),
    path('main/gcptest/', Upload_Receipt),
    path('main/return_receipt_img_List/', ReturnReceiptImgList.as_view()),
    path('main/receipt_url/', NewReceiptURL.as_view()),
    path('main/receipt_date/', ReceiptDate.as_view()),
    path('main/imagecache/', ImageCache.as_view()),
]
