from datetime import datetime, timezone

from django.db import models


class TimedModelMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.updated = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True