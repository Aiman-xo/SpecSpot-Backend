from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import timedelta
import uuid
from django.utils import timezone


# Create your models here.

class CustomManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not name:
            raise ValueError("Name is required")
        if not email:
            raise ValueError('please give the email')
        # convert it into lowercase if any type of email is given
        email = self.normalize_email(email)
        # create the user instance using email and name without saving to the model
        user = self.model(email=email, name=name, **extra_fields)
        # change the string password into hashed password only after that authentication
        user.set_password(password)
        user.save(using=self._db)  # saves the user into the db
        return user

    def create_superuser(self, email, password=None, name=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)  # set is_staff = True
        extra_fields.setdefault("is_superuser", True)

        # name = extra_fields.pop("name")
        if name is None:
            name = 'admin'
        return self.create_user(email=email, name=name, password=password, **extra_fields)


class Customer(AbstractUser):
    username = None

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=10,
        choices=[('Active', 'Active'), ('Blocked', 'Blocked')],
        default='Active'
    )
    signup_date = models.DateField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomManager()

    def __str__(self):
        return self.name
    

# class PasswordResetOTP(models.Model):
#     user = models.ForeignKey(Customer,on_delete=models.PROTECT)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     reset_session = models.UUIDField(default=uuid.uuid4,unique=True)
#     is_verified = models.BooleanField(default=False)

#     def is_expired(self):
#         return timezone.now() > self.created_at + timedelta(minutes=5)

class PasswordResetOtp(models.Model):
    user = models.ForeignKey(Customer,on_delete=models.PROTECT)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_session = models.UUIDField(default=uuid.uuid4,unique=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)