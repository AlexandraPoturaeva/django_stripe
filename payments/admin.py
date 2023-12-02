from django.contrib import admin
from .models import Item, Order, Tax

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Tax)
