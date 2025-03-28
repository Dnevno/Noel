from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Userdata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    displayed_name = models.CharField(max_length=20, null=True)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    date_of_birth = models.DateField(null=True)
    is_doctor = models.BooleanField(default=False)

class Qualification(models.Model):
    user = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=20)
    institution = models.CharField(max_length=20)
    year = models.DateField(null=True)

class MedicalHistory(models.Model):
    patient = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='medical_histories_as_patient')
    doctor = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='medical_histories_as_doctor')
    hospital = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    blood_pressure = models.CharField(max_length=20)
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=2)
    cholesterol = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(max_length=255)

class Share(models.Model):
    patient = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    shared_with = models.CharField(max_length=11, null=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.end_date = timezone.now() + timedelta(days=30)
        super(Share, self).save(*args, **kwargs)