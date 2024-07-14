from celery import shared_task
from django.core.mail import EmailMessage

@shared_task
def send_email_task(to_email, subject, message, attachment=None):
    email = EmailMessage(subject, message, 'your_email@example.com', [to_email])
    if attachment:
        email.attach('report.pdf', attachment, 'application/pdf')
        email.send()
