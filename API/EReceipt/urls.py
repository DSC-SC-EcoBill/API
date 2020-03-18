from django.urls import path
from .views import HelloAPI, SignupAPI, SignIn, Upload_Receipt, ReturnImg, ReturnList, ReturnItemImg, \
    ReturnReceiptImgList, NewReceiptURL, ReceiptDate, ImageCache
from .views import *

urlpatterns = [
    path('hello/', HelloAPI),
    path('auth/signup/', SignupAPI.as_view()),
    path('auth/signin/', SignIn),
    # path('main/upload_receipt/', Upload_Receipt),
    path('main/rimg/', ReturnImg),
    path('main/rlist/<int:user>/', ReturnList),
    path('main/ritemimg/', ReturnItemImg),
    path('main/return_receipt_img_List/', ReturnReceiptImgList.as_view()),
    path('main/receipt_url/', NewReceiptURL.as_view()),
    path('main/receipt_date/', ReceiptDate.as_view()),
    path('main/imagecache/', ImageCache.as_view()),
]
