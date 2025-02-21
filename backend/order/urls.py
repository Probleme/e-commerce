from django.urls import path
from .views import OrderListView, OrderDetailView, ShippingAddressListView, ShippingAddressDetailView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('shipping-addresses/', ShippingAddressListView.as_view(), name='shipping-address-list'),
    path('shipping-addresses/<int:pk>/', ShippingAddressDetailView.as_view(), name='shipping-address-detail'),
]