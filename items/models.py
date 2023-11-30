from django.db import models
from core.models import TimeStampedModel


class Item(TimeStampedModel):
    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at', 'name']

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def get_price_display(self):
        return "{0:.2f}".format(self.price / 100)
