from django.conf import settings
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, render, redirect
from .models import Item
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class ItemDetailView(View):
    def get(self, request, item_id):
        if not request.session.session_key:
            request.session.create()
        print(request.session.session_key)
        context = {
            'item': get_object_or_404(Item, pk=item_id),
        }
        return render(request, 'item.html', context=context)


class CreateStripeCheckoutSessionForItemView(View):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": item.price,
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={"product_id": item.id},
            mode="payment",
            success_url=settings.BACKEND_DOMAIN + '/success-payment/',
            cancel_url=settings.BACKEND_DOMAIN + '/cancel-payment/',
        )
        return redirect(checkout_session.url)


class SuccessPaymentView(TemplateView):
    template_name = 'success_payment.html'


class CancelPaymentView(TemplateView):
    template_name = 'cancel_payment_view'
