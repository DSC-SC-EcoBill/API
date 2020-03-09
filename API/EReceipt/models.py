from django.db import models


# Create your models here.
class Users(models.Model):
    # 모든 테이블의 id(pk)는 자동적으로 auto_increment로 생성
    user_id = models.CharField(max_length=16)
    password = models.CharField(max_length=40)
    name = models.CharField(max_length=16)
    jumin_no = models.IntegerField(null=True)
    email = models.CharField(max_length=64)


class Devices(models.Model):
    device_date = models.DateTimeField(auto_now_add=True)  # inseart한 현재시간 자동저장


class Receipt(models.Model):
    receipt_img_url = models.CharField(max_length=1000)
    receipt_date = models.DateTimeField(auto_now_add=True)
    flag = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)


class Qrcodes(models.Model):
    qrcode_img_url = models.CharField(max_length=1000)
    qrcode_date = models.DateTimeField(auto_now_add=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)


class Logs(models.Model):
    receipt_img_url = models.CharField(max_length=1000)
    log_generated_dt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)


