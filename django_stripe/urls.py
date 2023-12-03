from django.contrib import admin
from django.urls import path
from payments.views import (
    ItemDetailView,
    ItemListView,
    ItemCheckoutSessionView,
    OrderCheckoutSessionView,
    OrderPaymentIntentView,
    PaymentIntentResultView,
    SuccessPaymentView,
    CancelPaymentView,
    add_item_to_order_view,
    change_order_status_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ItemListView.as_view(), name='all_items'),
    path('item/<int:item_id>/', ItemDetailView.as_view(), name='item_details'),
    path(
        'buy/<int:item_id>/',
        ItemCheckoutSessionView.as_view(),
        name='buy_item',
    ),
    path(
        'pay-order/',
        OrderCheckoutSessionView.as_view(),
        name='pay_order',
    ),
    path(
        'success-payment/',
        SuccessPaymentView.as_view(),
        name='success_payment',
    ),
    path('cancel-payment/', CancelPaymentView.as_view()),
    path(
        'add-item-to-order/',
        add_item_to_order_view,
        name='add_item_to_order',
    ),
    path(
        'pay-order-with-payment-intent/<int:order_id>/',
        OrderPaymentIntentView.as_view(),
        name='order_payment_intent',
    ),
    path('change-order-status/', change_order_status_view),
    path('payment-intent-result/', PaymentIntentResultView.as_view()),
]
