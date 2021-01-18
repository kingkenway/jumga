# import deliva.load # Save json city files to db
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Shop, ShopCategory, Product, Order, OrderedItem, Transaction, Payment
# from django.conf import settings

User = get_user_model()


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rider', 'name', 'description', 'sub_domain', 'delivery_fee',
                    'logo', 'banner_image', 'is_active', 'updated_at', 'created_at', )


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'shop', 'is_active', 'created_at', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'description', 'slug', 'image', 'shop',
                    'shopcategory', 'is_active', 'updated_at', 'created_at', )


class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    # extra = 2


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'customer_name', 'customer_email',
                    'customer_contact', 'customer_address',
                    'customer_city', 'reference_id', 'paid',
                    'status', 'updated_at', 'created_at', )

    inlines = (OrderedItemInline,)


@admin.register(OrderedItem)
class OrderedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'quantity', 'item_price', )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'currency', 'merchant', 'shop',
                    'status', 'flw_ref', 'transaction_id',
                    'tx_ref', 'payment_type', 'order', 'narration',
                    'updated_at', 'created_at', )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'currency', 'beneficiary',
                    'transaction_id', 'transaction_type',
                    'tx_ref_from_payment', 'narration',
                    'updated_at', 'created_at', )
