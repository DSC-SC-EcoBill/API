from django.urls import path
from .views import HelloAPI, SignUp, SignIn, MakeQR, ReturnImg, ReturnList

urlpatterns = [
    path('hello/', HelloAPI),

    path('user/signup/', SignUp),
    path('user/signin/', SignIn),
    path('main/makeqr/', MakeQR),
    path('main/rimg/', ReturnImg),
    path('main/rlist/', ReturnList),
]
