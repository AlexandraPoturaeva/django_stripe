from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Item, Order, ItemsInOrder
from django.db.models import Sum
from .services import (
    get_session_id,
    process_payment_with_stripe_checkout,
    get_item_from_new_order,
    process_payment_intent,
    get_all_items_in_order,
    calculate_order_total_cost,
    calculate_number_of_items_in_order,
)


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
        order_total_cost = 0
        order_id = None

        session_id = get_session_id(request)
        unpaid_order = Order.objects.filter(
            session_id=session_id,
            status='NP',
        ).first()

        if unpaid_order:
            items_in_order = ItemsInOrder.objects.filter(
                order=unpaid_order,
            ).select_related("item")

            items_in_order_cnt = items_in_order.aggregate(
                Sum("quantity"),
            )['quantity__sum']

            order_id = unpaid_order.id

            order_total_cost = sum([
                item.item.price * item.quantity
                for item in items_in_order
            ]) / 100

        context = {
            'all_items': all_items,
            'items_in_order_cnt': items_in_order_cnt,
            'order_total_cost': order_total_cost,
            'order_id': order_id,
        }

        return render(request, 'item_list.html', context=context)


class ItemCheckoutSessionView(View):
    def get(self, request, item_id):
        item = get_item_from_new_order(request=request, item_id=item_id)
        return process_payment_with_stripe_checkout(items=[item])


@require_POST
def add_item_to_order_view(request):
    """
    View to add the item into unpaid order. It gets post request through ajax.
    If there is no unpaid order for this session, the order will be created.
    If there already is such item in the order,
    it's quantity will be increased by 1.
    View returns total cost of order,
    total quantity of items in order and order_id
    back to ajax in JsonResponse.
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

    all_items_in_order = get_all_items_in_order(order.id)
    items_in_order_cnt = calculate_number_of_items_in_order(all_items_in_order)
    order_total_cost = calculate_order_total_cost(all_items_in_order)

    data = {
        'items_in_order_cnt': items_in_order_cnt,
        'order_total_cost': order_total_cost,
        'order_id': order.id,
    }

    return JsonResponse(data)


class OrderCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        session_id = get_session_id(request)

        order = Order.objects.filter(
            session_id=session_id,
            status='NP',
        ).first()

        items_in_order = get_all_items_in_order(order.id)

        return process_payment_with_stripe_checkout(items=items_in_order)


class SuccessPaymentView(TemplateView):
    template_name = 'success_payment.html'


class CancelPaymentView(TemplateView):
    template_name = 'cancel_payment_view'


class OrderPaymentIntentView(View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['order_id']
        all_items_in_order = get_all_items_in_order(order_id)
        order_total_cost = round(
            calculate_order_total_cost(all_items_in_order) * 100,
        )
        return process_payment_intent(price=order_total_cost)


@require_POST
def change_order_status_view(request):
    order_id = request.POST.get('order_id')
    order = Order.objects.get(id=order_id)
    order.status = 'P'
    order.save()
    return JsonResponse({'message': 'Payment succeeded!'})


class PaymentIntentResultView(TemplateView):
    template_name = 'payment_intent_result.html'
