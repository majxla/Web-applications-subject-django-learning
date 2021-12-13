import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from core.models import TimestampedModel

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, type, password=None):
        user = None
        
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have a email address.')
        

        if type == "patient":
            user = Patient.objects.create(username = username, email=self.normalize_email(email))
        elif type == "doctor":
            user = Doctor.objects.create(username = username, email=self.normalize_email(email))
        
        if user:
            user.set_password(password)
            user.save()

        return user
    
    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11)

    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    
    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
    
    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
    

class Specialisation(models.Model):
    spec_name = models.CharField(max_length=50, default='')

    class Meta:
        ordering = ['spec_name']

    def __str__(self):
        return self.spec_name

class Patient(User):
    pesel = models.CharField(max_length=11, default="")

class Doctor(User):
    specialization = models.ManyToManyField(Specialisation)

class Visit(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, default='')
    date = models.DateTimeField(default='')

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.doctor, self.address, self.date
