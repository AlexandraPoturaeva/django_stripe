from django.contrib import admin
from django.urls import include, path
from payments.views import (
    BuyItemView,
    BuyOrderView,
    SuccessPaymentView,
    CancelPaymentView,
    add_item_to_order_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('item/', include('payments.urls')),
    path(
        'buy/<int:item_id>/',
        BuyItemView.as_view(),
        name='buy_item',
    ),
    path(
        'buy-order/',
        BuyOrderView.as_view(),
        name='buy_order',
    ),
    path('success-payment/', SuccessPaymentView.as_view()),
    path('cancel-payment/', CancelPaymentView.as_view()),
    path(
        'add-item-to-order/',
        add_item_to_order_view,
        name='add_item_to_order',
    ),
]
