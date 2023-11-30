from django.contrib import admin
from django.urls import include, path
from items.views import (
    CreateStripeCheckoutSessionForItemView,
    SuccessPaymentView,
    CancelPaymentView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('item/', include('items.urls')),
    path(
        'buy/<int:item_id>/',
        CreateStripeCheckoutSessionForItemView.as_view(),
        name='create-checkout-session',
    ),
    path('success-payment/', SuccessPaymentView.as_view()),
    path('cancel-payment/', CancelPaymentView.as_view()),
]
