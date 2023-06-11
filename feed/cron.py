from django_cron import CronJobBase, Schedule
from django.utils import timezone

from feed.models import GroupPurchase


class PurchaseCronJob(CronJobBase):
    pass
    # RUN_TIME = ["00:00"]
    # schedule = Schedule(run_at_times=RUN_TIME)
    # code = "feed.purchase_cron_job"

    # def do(self):
    #     six_months_ago = timezone.now() - timezone.timedelta(days=180)
    #     one_year_ago = timezone.now() - timezone.timedelta(days=365)
    #     five_years_ago = timezone.now() - timezone.timedelta(days=1825)

    #     dormant_users = User.objects.filter(last_login__lt=one_year_ago).update(
    #         is_dormant=True
    #     )
    #     if dormant_users:
    #         for user in dormant_users:
    #             pass

    #     User.objects.filter(withdraw_at__lt=five_years_ago).delete()

    #     user_pwd_expiry = User.objects.filter(change_password_at=six_months_ago)
    #     if user_pwd_expiry:
    #         for user in user_pwd_expiry:
    #             pass
