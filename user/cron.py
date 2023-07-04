from django_cron import CronJobBase, Schedule
from django.utils import timezone

from .models import User
from .tasks import information_email


class MyCronJob(CronJobBase):
    RUN_TIME = ["00:00"]
    schedule = Schedule(run_at_times=RUN_TIME)
    code = "user.my_cron_job"

    def do(self):
        eleven_months_ago = timezone.now() - timezone.timedelta(days=330)
        eleven_months_one_age = timezone.now() - timezone.timedelta(days=329)
        one_year_ago = timezone.now() - timezone.timedelta(days=365)
        five_years_ago = timezone.now() - timezone.timedelta(days=1825)

        User.objects.filter(last_login__lt=one_year_ago).update(is_dormant=True)
        pre_dormants = User.objects.filter(
            last_login__lt=eleven_months_ago,
            last_login__gt=eleven_months_one_age,
            is_dormant=False,
        )
        recipient_list = []
        for pre_dormant in pre_dormants:
            email = pre_dormant.email
            recipient_list.append(email)
        subject = "회원님의 계정이 1달뒤에 휴면계정 처리 될 예정입니다"
        message = "회원님의 활동이 없어서 계정이 1달뒤에 휴면계정 처리가 될 예정입니다. 계정을 활성화 하시려면 로그인을 해주세요."
        information_email.delay(subject, message, recipient_list)

        User.objects.filter(withdraw_at__lt=five_years_ago).delete()
