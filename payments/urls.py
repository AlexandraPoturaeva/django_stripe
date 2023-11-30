from django.urls import path
from .views import ItemDetailView

urlpatterns = [
    path('<int:item_id>/', ItemDetailView.as_view()),
]
