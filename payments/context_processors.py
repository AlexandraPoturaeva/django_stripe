from django.conf import settings


def stripe_pk_processor(request):
    return {
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    }


def backend_domain_processor(request):
    return {
        'backend_domain': settings.BACKEND_DOMAIN,
    }
