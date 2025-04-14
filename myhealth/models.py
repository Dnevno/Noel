from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from myhealth.utils.crypto import CryptoUtils

# Create your models here.
class Userdata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    displayed_name = models.CharField(max_length=20, null=True)
    _phone = models.BinaryField(db_column="phone", editable=False, null=True)
    phone_hash = models.CharField(max_length=64, db_index=True, null=True)
    _address = models.BinaryField(db_column="address", editable=False, null=True)
    _date_of_birth = models.BinaryField(db_column="date_of_birth", editable=False, null=True)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.displayed_name if self.displayed_name else self.user.username

    @property
    def phone(self):
        return CryptoUtils.decrypt(self._phone) if self._phone else None
    
    @phone.setter
    def phone(self, value):
        if value:
            self._phone = CryptoUtils.encrypt(value)
            self.phone_hash = CryptoUtils.hash(value)
        else:
            self._phone = None
            self.phone_hash = None

    @property
    def address(self):
        return CryptoUtils.decrypt(self._address) if self._address else None
    
    @address.setter
    def address(self, value):
        self._address = CryptoUtils.encrypt(value) if value else None

    @property
    def date_of_birth(self):
        return CryptoUtils.decrypt(self._date_of_birth) if self._date_of_birth else None
    
    @date_of_birth.setter
    def date_of_birth(self, value):
        self._date_of_birth = CryptoUtils.encrypt(value) if value else None

class Qualification(models.Model):
    user = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=20)
    institution = models.CharField(max_length=20)
    year = models.DateField(null=True)

    def __str__(self):
        return f"{self.qualification} from {self.user.username}"

class MedicalHistory(models.Model):
    patient = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='medical_histories_as_patient')
    doctor = models.ForeignKey(Userdata, on_delete=models.CASCADE, related_name='medical_histories_as_doctor')
    hospital = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)
    
    _weight = models.BinaryField(db_column="weight", editable=False, null=True)
    _height = models.BinaryField(db_column="height", editable=False, null=True)
    _blood_pressure = models.BinaryField(db_column="blood_pressure", editable=False, null=True)
    _blood_sugar = models.BinaryField(db_column="blood_sugar", editable=False, null=True)
    _cholesterol = models.BinaryField(db_column="cholesterol", editable=False, null=True)
    _notes = models.BinaryField(db_column="notes", editable=False, null=True)

    def __str__(self):
        return f"Medical history of {self.patient.displayed_name} by {self.doctor.displayed_name} on {self.date}"
    
    @property
    def weight(self):
        decrypted = CryptoUtils.decrypt(self._weight)
        return float(decrypted) if decrypted is not None else None
    
    @weight.setter
    def weight(self, value):
        self._weight = CryptoUtils.encrypt(value) if value else None
    
    @property
    def height(self):
        decrypted = CryptoUtils.decrypt(self._height)
        return float(decrypted) if decrypted is not None else None
    
    @height.setter
    def height(self, value):
        self._height = CryptoUtils.encrypt(value) if value else None

    @property
    def blood_pressure(self):
        return CryptoUtils.decrypt(self._blood_pressure) if self._blood_pressure is not None else None
    
    @blood_pressure.setter
    def blood_pressure(self, value):
        self._blood_pressure = CryptoUtils.encrypt(value) if value else None

    @property
    def blood_sugar(self):
        decrypted = CryptoUtils.decrypt(self._blood_sugar)
        return float(decrypted) if decrypted is not None else None
    
    @blood_sugar.setter
    def blood_sugar(self, value):
        self._blood_sugar = CryptoUtils.encrypt(value) if value else None

    @property
    def cholesterol(self):
        decrypted = CryptoUtils.decrypt(self._cholesterol)
        return float(decrypted) if decrypted is not None else None
    
    @cholesterol.setter
    def cholesterol(self, value):
        self._cholesterol = CryptoUtils.encrypt(value) if value else None

    @property
    def notes(self):
        return CryptoUtils.decrypt(self._notes) if self._notes else None
    
    @notes.setter
    def notes(self, value):
        self._notes = CryptoUtils.encrypt(value) if value else None

class Share(models.Model):
    patient = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    shared_with = models.CharField(max_length=11, null=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Share record for {self.patient.displayed_name} with {self.shared_with} on {self.shared_at}"

    def save(self, *args, **kwargs):
        self.end_date = timezone.now() + timedelta(days=30)
        super(Share, self).save(*args, **kwargs)