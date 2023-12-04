from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models.query import QuerySet
from django.db.models import Sum
from .models import Item, ItemsInOrder, Tax, Discount, Order
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_session_id(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def get_item_from_new_order(request, item_id):
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

    return item_in_order


def get_all_items_in_order(order_id: int):
    return ItemsInOrder.objects.filter(
        order=order_id,
    ).select_related("item")


def calculate_order_total_cost(items: QuerySet[Item]) -> int:
    order_total_cost = sum([
        item.item.price * item.quantity
        for item in items
    ]) / 100

    return order_total_cost


def calculate_number_of_items_in_order(items: QuerySet[Item]) -> int:
    num_of_items = items.aggregate(
        Sum("quantity"),
    )['quantity__sum']

    return num_of_items


def create_stripe_tax_rate(order: Order) -> stripe.TaxRate:
    tax_rate = stripe.TaxRate.create(
        display_name=order.tax.display_name,
        inclusive=order.tax.inclusive,
        percentage=order.tax.percentage,
    )
    return tax_rate


def create_stripe_coupon(order: Order) -> stripe.Coupon:
    coupon = stripe.Coupon.create(
        percent_off=order.discount.percent_off,
        duration=order.discount.duration,
    )
    return coupon


def create_stripe_checkout_session(
        line_items: list[dict],
        order_id: int,
        coupon_id: str,
) -> stripe.checkout.Session:
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        metadata={'type': 'order', 'id': order_id},
        discounts=[{'coupon': coupon_id}],
        mode='payment',
        success_url=settings.BACKEND_DOMAIN + '/success-payment/',
        cancel_url=settings.BACKEND_DOMAIN + '/cancel-payment/',
    )
    return checkout_session


def process_payment_with_stripe_checkout(
        items: QuerySet[Item] | list[Item],
) -> HttpResponse:
    """
    Create stripe checkout session, change status of the order
    and redirect the user to Stripe's checkout page
    :param items: QuerySet[Item] | list[Item]
    :return: HttpResponse
    """
    order = items[0].order
    tax, created = Tax.objects.get_or_create(
        display_name='Sales Tax',
        percentage=20.0,
    )
    discount, created = Discount.objects.get_or_create(
        percent_off=10.0,
        duration='once',
    )
    order.tax = tax
    order.discount = discount

    try:
        tax_rate = create_stripe_tax_rate(order)
    except Exception:
        return HttpResponse(status=500)

    try:
        coupon = create_stripe_coupon(order)
    except Exception:
        return HttpResponse(status=500)

    line_items = []
    for item in items:
        item_data = {
            'price_data': {
                'currency': 'usd',
                'unit_amount': item.item.price,
                'product_data': {
                    'name': item.item.name,
                    'description': item.item.description,
                },
            },
            'quantity': item.quantity,
            'tax_rates': [tax_rate.id],
        }
        line_items.append(item_data)

    try:
        checkout_session = create_stripe_checkout_session(
            line_items=line_items,
            order_id=order.id,
            coupon_id=coupon.id,
        )
    except Exception:
        return HttpResponse(status=500)

    order.status = 'P'
    order.save()

    return redirect(checkout_session.url)


def process_payment_intent(price: int) -> JsonResponse:
    try:
        intent = stripe.PaymentIntent.create(
            amount=price,
            currency='usd',
        )
        print(intent['client_secret'])
        return JsonResponse({
            'clientSecret': intent['client_secret'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
