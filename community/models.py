from django.db import models
from user.models import User


class Community(models.Model):
    class Meta:
        db_table = "community"

    title = models.CharField(max_length=20)
    introduction = models.TextField()
    is_approval = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)


class CommunityAdmin(models.Model):
    class Meta:
        db_table = "community_admin"

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
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
