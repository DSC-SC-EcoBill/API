# Generated by Django 3.0.4 on 2020-04-27 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EReceipt', '0003_auto_20200427_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='receipt_img_uri',
            field=models.TextField(default=''),
        ),
    ]