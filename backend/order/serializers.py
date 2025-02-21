from rest_framework import serializers
from .models import Order, OrderItem, ShippingAddress

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ('id', 'street_address', 'city', 'state', 'postal_code', 'country', 'phone')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'unit_price', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'order_status', 'order_date', 'shipping_address', 'items')

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address = ShippingAddressSerializer()

    class Meta:
        model = Order
        fields = ('total_price', 'shipping_address', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shipping_address_data = validated_data.pop('shipping_address')
        shipping_address = ShippingAddress.objects.create(**shipping_address_data)
        order = Order.objects.create(shipping_address=shipping_address, **validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order