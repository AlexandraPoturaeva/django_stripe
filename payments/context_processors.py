from django.conf import settings


def stripe_pk_processor(request):
    return {
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    }
