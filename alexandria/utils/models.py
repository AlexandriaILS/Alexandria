from django.db import models
from django.utils import timezone


class TimeStampMixin(models.Model):
    # https://stackoverflow.com/a/57971729
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Sometimes self.updated_at doesn't update automatically; I don't know why.
        # This shouldn't be needed, but it fixes the issue as far as I can see.
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
