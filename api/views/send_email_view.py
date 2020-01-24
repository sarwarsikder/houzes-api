from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from houzes_api import settings

class SendEmailViewSet():
    def send_email_view(self,subject,message,email,receiver_name,url):
        try:
            print('::::::::::::::::SEND EMAIL STARTED::::::::::::::::::::::::::')
            subject, from_email, to = subject, settings.EMAIL_HOST_USER, email
            text_content = '<strong>This is an important message.</strong>'
            html_content = render_to_string("send_email.html",{'url' : url,
                                                               'receiver_name' : receiver_name,
                                                               'message' : message})
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except:
            print('Email sending failed')