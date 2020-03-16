from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Devices(models.Model):
    device_date = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=8, default='')


class Receipt(models.Model):
    receipt_img_url = models.TextField(default='')
    receipt_date = models.DateTimeField(auto_now_add=True)
    qr_url = models.TextField(default='')
    flag = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Qrcodes(models.Model):
    qrcode_img_url = models.TextField(default='')
    qrcode_date = models.DateTimeField(auto_now_add=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
