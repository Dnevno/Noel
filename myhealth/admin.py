from django.contrib import admin
from .models import Userdata, Qualification, MedicalHistory, Share

# Register your models here.
admin.site.register(Userdata)
admin.site.register(Qualification)
admin.site.register(MedicalHistory)
admin.site.register(Share)
