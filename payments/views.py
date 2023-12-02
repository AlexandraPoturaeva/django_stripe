from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Item, Order, ItemsInOrder
from django.db.models import Sum
from .services import get_session_id, process_payment
import json


class ItemDetailView(View):
    def get(self, request, item_id):
        context = {
            'item': get_object_or_404(Item, pk=item_id),
        }
        return render(request, 'item.html', context=context)


class ItemListView(View):
    def get(self, request):
        all_items = Item.objects.all()
        items_in_order_cnt = 0

        session_id = get_session_id(request)
        unpaid_order = Order.objects.filter(
            session_id=session_id,
            status='NP',
        ).first()
        items_in_order = ItemsInOrder.objects.filter(
            order=unpaid_order,
        ).select_related("item")
        if items_in_order:
            items_in_order_cnt = items_in_order.aggregate(
                Sum("quantity"),
            )['quantity__sum']
        order_total_cost = sum([
            item.item.price * item.quantity
            for item in items_in_order
        ]) / 100

        context = {
            'all_items': all_items,
            'items_in_order_cnt': items_in_order_cnt,
            'order_total_cost': order_total_cost,
        }

        return render(request, 'item_list.html', context=context)


class BuyItemView(View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)
        session_id = get_session_id(request)
        order = Order.objects.create(
            session_id=session_id,
            status='NP',
        )
        item_in_order = ItemsInOrder.objects.create(
            order=order,
            item=item,
            quantity=1,
        )

        return process_payment(items=[item_in_order])


@require_POST
def add_item_to_order_view(request):
    """
    View to add the item to an unpaid order. It gets post request through ajax.
    If there is no an unpaid order for this session, the order will be created.
    If there already is such item in the order,
    it's quantity will be increased by 1.
    View returns total cost of order and total quantity of items in order
    back to ajax in HttpResponse.
    :param request: HttpRequest
    :return: HttpResponse
    """
    item_id = request.POST.get('item_id')
    session_id = get_session_id(request)
    order, created = Order.objects.get_or_create(
        session_id=session_id,
        status='NP',
    )
    item_in_order, created = ItemsInOrder.objects.get_or_create(
        order_id=order.id, item_id=item_id,
    )
    item_in_order.quantity += 1
    item_in_order.save()

    all_items_in_order = ItemsInOrder.objects.filter(
        order=order,
    ).select_related("item")
    items_in_order_cnt = all_items_in_order.aggregate(
        Sum("quantity"),
    )['quantity__sum']
    order_total_cost = sum([
        item.item.price * item.quantity
        for item in all_items_in_order
    ]) / 100
    data = json.dumps({
        "items_in_order_cnt": items_in_order_cnt,
        "order_total_cost": order_total_cost,
    })

    return HttpResponse(data, content_type="application/json")


class BuyOrderView(View):
    def post(self, request, *args, **kwargs):
        session_id = get_session_id(request)
        order = Order.objects.filter(
            session_id=session_id,
            status='NP',
        ).first()
        items_in_order = ItemsInOrder.objects.filter(
            order=order,
        ).select_related('item')

        return process_payment(items=items_in_order)


class SuccessPaymentView(TemplateView):
    template_name = 'success_payment.html'


class CancelPaymentView(TemplateView):
    template_name = 'cancel_payment_view'
