from celery import shared_task
from .models import Feed, Image
import re
import os
from django.core.files.storage import default_storage


@shared_task
def image_delete_job():
    feeds = Feed.objects.all()
    used_image_url = []
    all_images = os.listdir("media/feed")
    for feed in feeds:
        content = feed.content
        image_tags = re.findall(r'<img.*?src="(.*?)".*?>', content)
        for image_tag in image_tags:
            image_name = image_tag.split("feed/")[1]
            used_image_url.append(image_name)
    for image in all_images:
        if image not in used_image_url:
            os.remove("media/feed/" + image)
