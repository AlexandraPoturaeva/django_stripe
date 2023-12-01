from django.urls import path
from .views import ItemDetailView, ItemListView

urlpatterns = [
    path('<int:item_id>/', ItemDetailView.as_view()),
    path('all/', ItemListView.as_view()),
]
