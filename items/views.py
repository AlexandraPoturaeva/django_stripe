from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from .models import Item


class ItemDetailView(View):
    def get(self, request, item_id):
        context = {
            'item': get_object_or_404(Item, pk=item_id),
        }
        return render(request, 'item.html', context=context)
