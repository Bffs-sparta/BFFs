from celery import shared_task
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail


@shared_task
def verifymail(email, code):
    subject = "BFFs 이메일 인증코드 메일입니다."
    from_email = config("EMAIL")

    html_content = render_to_string("verfication.html", {"code": code})
    send_email = EmailMessage(subject, html_content, from_email, [email])
    send_email.content_subtype = "html"
    send_email.send()


@shared_task
def pwresetMail(email, reset_url):
    send_mail(
        subject="BFFs 비밀번호 변경 메일",
        message=f"비밀번호 변경을 위해 해당링크를 클릭해주세요: {reset_url}",
        from_email="sender@example.com",
        recipient_list=[email],
    )
