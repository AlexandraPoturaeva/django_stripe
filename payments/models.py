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


class Order(TimeStampedModel):
    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']

    items = models.ManyToManyField(Item, through='ItemsInOrder')
    status = models.CharField(
        max_length=2,
        choices=[
            ('NP', 'Not paid'),
            ('P', 'Paid'),
        ],
        default='NP',
    )
    session_id = models.CharField(
        max_length=40,
        null=False,
    )

    def __str__(self):
        return f"Order #{self.pk} " \
               f"placed on " \
               f"{self.created_at.strftime('%d.%m.%y %H:%M:%S')}"


class ItemsInOrder(TimeStampedModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=0)
