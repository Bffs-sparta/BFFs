from django_cron import CronJobBase, Schedule
from django.utils import timezone

from feed.models import GroupPurchase


class MyPurchaseCronJob(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "feed.my_purchase_job"

    def do(self):
        now = timezone.now()
        code = "feed.my_purchase_job"

        end_grouppuchase = GroupPurchase.objects.filter(close_at__gte=now).update(
            is_ended=True
        )
        # print("⭐️공구 마감⭐️")
