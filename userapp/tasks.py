from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_registration_email(self, email, name):
    subject = "Welcome to our site"
    message = (
        f"Hello {name},\n\n"
        f"Thank you for registering with us!\n"
        f"Happy shopping!"
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5}
)
def send_otp_email(self, email, otp):
    subject = "Your requested password reset OTP"
    message = (
        f"Hello {email},\n\n"
        f"OTP: {otp}\n"
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )