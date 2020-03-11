from django.db import models


# Create your models here.
class Guests(models.Model):
    # 모든 테이블의 id(pk)는 자동적으로 auto_increment로 생성
    guest_id = models.CharField(max_length=16)
    guest_password = models.CharField(max_length=40)
    name = models.CharField(max_length=16)
    jumin_no = models.IntegerField(null=True)
    email = models.EmailField(default="email@example.com")


class Devices(models.Model):
    device_id = models.CharField(max_length=16)
    device_password = models.CharField(max_length=40)
    device_date = models.DateTimeField(auto_now_add=True)  # inseart한 현재시간 자동저장


class Receipt(models.Model):
    receipt_img_url = models.TextField()
    receipt_date = models.DateTimeField(auto_now_add=True)
    qr_url = models.TextField()
    flag = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)


class Qrcodes(models.Model):
    qrcode_img_url = models.TextField()
    qrcode_date = models.DateTimeField(auto_now_add=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)