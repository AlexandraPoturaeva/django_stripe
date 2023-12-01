from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from .models import Item
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_session_id(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def create_checkout_session(
        items: QuerySet[Item] | list[Item],
) -> HttpResponse:
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    :param items: QuerySet[Item] | list[Item]
    :return: HttpResponse
    """
    order = items[0].order

    line_items = []
    for item in items:
        item_data = {
            "price_data": {
                "currency": "usd",
                "unit_amount": item.item.price,
                "product_data": {
                    "name": item.item.name,
                    "description": item.item.description,
                },
            },
            "quantity": item.quantity,
        }
        line_items.append(item_data)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            metadata={"type": "order", "id": order.id},
            mode="payment",
            success_url=settings.BACKEND_DOMAIN + '/success-payment/',
            cancel_url=settings.BACKEND_DOMAIN + '/cancel-payment/',
        )
        order.status = 'P'
        order.save()
    except Exception:
        return HttpResponse(status=500)

    return redirect(checkout_session.url)
