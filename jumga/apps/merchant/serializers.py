from django.contrib.auth import get_user_model
from rest_framework import serializers
from six import text_type
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Shop, ShopCategory, Product, Order, OrderedItem, Transaction, Payment
from django.db import transaction, IntegrityError

User = get_user_model()


class ShopSerializer(serializers.ModelSerializer):

    rider = serializers.ReadOnlyField(source='rider_full_name')

    class Meta:
        model = Shop
        fields = ['id', 'user', 'name', 'rider', 'description', 'sub_domain', 'delivery_fee',
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


class ShopAndProductsSerializer(serializers.ModelSerializer):
    country = serializers.ReadOnlyField(source='country_data')
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'user', 'name', 'description', 'sub_domain', 'delivery_fee',
                  'logo', 'banner_image', 'is_active', 'country', 'products']


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'merchant', 'shop',
                  'status', 'flw_ref', 'transaction_id',
                  'tx_ref', 'payment_type', 'order',
                  'updated_at', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'currency', 'beneficiary', 'transaction_id',
                  'transaction_type', 'tx_ref_from_payment', 'narration', 'created_at']
        depth = 1


class ShopNestedSerializer(serializers.ModelSerializer):
    country = serializers.ReadOnlyField(source='country_data')

    class Meta:
        model = Shop
        fields = ['id', 'name', 'country']


class CustomerOrdersSerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField(source='get_total_cost')
    shop = ShopNestedSerializer()

    class Meta:
        model = Order
        fields = ['id', 'shop', 'customer_email', 'customer_city',
                  'status', 'total_amount', 'reference_id', 'created_at']
        depth = 1


class MerchantOrdersSerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField(source='get_total_cost')
    shop = ShopNestedSerializer()

    class Meta:
        model = Order
        fields = ['id', 'shop', 'customer_name', 'customer_contact', 'customer_email', 'customer_city',
                  'status', 'total_amount', 'reference_id', 'items', 'created_at']
        depth = 2


class ExtraFieldSerializer(serializers.Field):
    def to_internal_value(self, data):
        return data

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        """
        Serialize the value's class name.
        """
        return value.__class__.__name__


class OrderSerializer(serializers.ModelSerializer):

    cart = ExtraFieldSerializer()
    total_amount = serializers.ReadOnlyField(source='get_total_cost')
    reference_id = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'shop', 'customer_name', 'customer_email',
                  'customer_contact', 'customer_address', 'customer_city',
                  'customer_instruction', 'updated_at', 'created_at',
                  'cart', 'total_amount', 'reference_id']

    def create(self, validated_data):
        with transaction.atomic():
            order = Order.objects.create(
                shop=validated_data['shop'],
                customer_name=validated_data['customer_name'],
                customer_email=validated_data['customer_email'],
                customer_contact=validated_data['customer_contact'],
                customer_address=validated_data['customer_address'],
                customer_city=validated_data['customer_city'],
                customer_instruction=validated_data['customer_instruction'],
            )
            cart = validated_data.pop('cart')

            for item in cart:
                # This query below is to get exact price incase
                #  you do not trust the price sent to
                # you by the front end. If you do, comment this line below  and
                # replace product.price with item['price]
                product = Product.objects.get(id=item['id'])
                OrderedItem.objects.create(
                    order=order,
                    product_id=item['id'],
                    quantity=item['quantity'],
                    item_price=product.price,
                )

            print(cart)

        return order
