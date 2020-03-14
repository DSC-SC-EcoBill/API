from django.urls import path
from .views import HelloAPI, SignUp, SignIn, Upload_Receipt, ReturnImg, ReturnList, ReturnItemImg

urlpatterns = [
    path('hello/', HelloAPI),

    path('user/signup/', SignUp),
    path('user/signin/', SignIn),
    path('main/upload_receipt/', Upload_Receipt),
    path('main/rimg/', ReturnImg),
    path('main/rlist/<int:user>/', ReturnList),
    path('main/ritemimg/', ReturnItemImg),
]
