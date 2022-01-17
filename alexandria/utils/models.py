from django.db import models


class TimeStampMixin(models.Model):
    # https://stackoverflow.com/a/57971729
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
