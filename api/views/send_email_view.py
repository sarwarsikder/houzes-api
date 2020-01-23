from django.core.mail import send_mail

from houzes_api import settings


class SendEmailViewSet():
    def send_email_view(self,subject,message,email):
        try:
            send_mail(subject=subject,
                      message=message,
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[email],
                      fail_silently=False
                      )
        except:
            print('Email sending failed')