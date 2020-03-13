from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Guests)
admin.site.register(Devices)
admin.site.register(Receipt)
admin.site.register(Qrcodes)

