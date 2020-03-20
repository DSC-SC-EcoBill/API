from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# 영수증 이미지
class Receipt(models.Model):
    receipt_img_url = models.TextField(default='')
    receipt_date = models.DateTimeField(auto_now_add=True)
    is_Storage = models.IntegerField(default=0)
    device_id = models.TextField(max_length=8, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Qrcodes(models.Model):
    qr_url = models.TextField(default='')
    qrcode_date = models.DateTimeField(auto_now_add=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)


# 영수증 이미지를 잠시 저장하는 모델
class ImageCache(models.Model):
    upload_data = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=20, default='')
    image_name = models.CharField(max_length=20, default='')
    image = models.ImageField(default='default_img.jpg')

