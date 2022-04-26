from django.db import models
from django.utils import timezone


class TimeStampMixin(models.Model):
    # https://stackoverflow.com/a/57971729
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
