from django_cron import CronJobBase, Schedule
from django.utils import timezone

from feed.models import GroupPurchase
from .tasks import image_delete_job


class ImageDeleteJob(CronJobBase):
    RUN_TIME = ["00:00"]
    schedule = Schedule(run_at_times=RUN_TIME)
    code = "feed.image_delete_job"

    def do(self):
        image_delete_job.delay()


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
