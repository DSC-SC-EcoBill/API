from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# 포스기마다 등록할 수 있는 모델
class Device(models.Model):
    brand_name = models.TextField(max_length=10, default='')


# 영수증 이미지
class Receipt(models.Model):
    receipt_img_url = models.TextField(default='')
    receipt_img_uri = models.TextField(default='')
    receipt_date = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(default=0)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)


# 확인 코드를 저장하는 모델
class VerifyCodes(models.Model):
    email = models.EmailField()
    verify_code = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)

