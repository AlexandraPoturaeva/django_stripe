from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from .models import Item, Tax, Discount, Order
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_session_id(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


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


def process_payment(
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
