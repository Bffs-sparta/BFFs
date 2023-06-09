from celery import shared_task
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def verifymail(email, code):
    subject = "BFFs 이메일 인증코드 메일입니다."
    from_email = config("EMAIL")

    html_content = render_to_string("verfication.html", {"code": code})
    send_email = EmailMessage(subject, html_content, from_email, [email])
    send_email.content_subtype = "html"
    send_email.send()


@shared_task
def pwresetMail(message):
    subject = message.get("subject")
    from_email = config("EMAIL")
    url = message.get("url")
    html_content = render_to_string("email.html", {"url": url})
    send_email = EmailMessage(subject, html_content, from_email, [message.get("email")])
    send_email.content_subtype = "html"
    send_email.send()
