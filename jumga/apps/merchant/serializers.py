from django.contrib.auth import get_user_model
from rest_framework import serializers
from six import text_type
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Shop, ShopCategory, Product, Order

User = get_user_model()


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['id', 'user', 'name', 'description', 'sub_domain', 'delivery_fee',
                  'logo', 'banner_image', 'is_active']

    def update(self, instance, validated_data):
        # prevent fields from being updated
        validated_data.pop('is_active', None)
        return super().update(instance, validated_data)


class ShopCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopCategory
        fields = ['id', 'name', 'slug', 'shop', 'is_active', 'created_at']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image', 'shop', 'slug',
                  'shopcategory', 'is_active', 'updated_at', 'created_at', ]


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'shop', 'customer', 'address', 'city', 'reference_id', 'paid',
                  'status', 'updated_at', 'created_at', ]
