from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from user.models import User


class Community(models.Model):
    class Meta:
        db_table = "community"

    def validate_image(self):
        if self.size > 5 * 1024 * 1024:
            raise ValueError("이미지의 크기는 5MB 이하여야 합니다.")

    title = models.CharField(max_length=20, unique=True)
    introduction = models.TextField()
    image = models.ImageField(
        upload_to="community_img/", null=True, blank=True, validators=[validate_image]
    )
    is_approval = models.BooleanField(default=False)

    bookmarked = models.ManyToManyField(User, related_name="bookmark", blank=True)

    def __str__(self):
        return str(self.title)


@receiver(pre_save, sender=Community)
def pre_save_receiver(sender, instance, **kwargs):
    if instance.pk is None:
        pass
    else:
        new = instance
        old = sender.objects.get(pk=instance.pk)
        if old.image and old.image != new.image:
            default_storage.delete(old.image.path)


class CommunityAdmin(models.Model):
    class Meta:
        db_table = "community_admin"

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="mycomu")
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="comu"
    )
    is_comuadmin = models.BooleanField(default=False)
    is_subadmin = models.BooleanField(default=False)


class ForbiddenWord(models.Model):
    class Meta:
        db_table = "community_forbiddenword"

    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="forbiddenword"
    )
    word = models.CharField(max_length=10)

    def __str__(self):
        return str(self.word)
