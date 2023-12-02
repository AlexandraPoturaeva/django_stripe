from django.db import models
from core.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator


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


class Tax(TimeStampedModel):
    display_name = models.CharField(max_length=10)
    inclusive = models.BooleanField()
    percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(0)],
    )
    country = models.CharField(null=True, blank=True, max_length=2)
    state = models.CharField(null=True, blank=True, max_length=50)
    jurisdiction = models.CharField(null=True, blank=True, max_length=100)
    description = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return f'{self.display_name} {self.percentage}%'


class Discount(TimeStampedModel):
    amount_off = models.PositiveSmallIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    duration = models.CharField(
        max_length=9,
        choices=[
            ('once', 'once'),
            ('repeating', 'repeating'),
            ('forever', 'forever'),
        ],
    )
    duration_in_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    metadata = models.JSONField(null=True, blank=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    percent_off = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        null=True,
        blank=True,
    )


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
    )
    taxes = models.ManyToManyField(Tax)
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"Order #{self.pk} " \
               f"placed on " \
               f"{self.created_at.strftime('%d.%m.%y %H:%M:%S')}"


class ItemsInOrder(TimeStampedModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=0)
