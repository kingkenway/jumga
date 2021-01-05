from decimal import Decimal as D
from jumga.extras import CharNullField
from jumga.apps.account.models import Merchant, Customer, Rider
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def approximate(val):
    return D(val).quantize(D('0.01'))


class Shop(models.Model):

    user = models.ForeignKey(
        Merchant, on_delete=models.CASCADE, related_name='shop')

    rider = models.ForeignKey(
        Rider, on_delete=models.CASCADE, blank=True, null=True)

    name = models.CharField(max_length=500)
    description = models.CharField(max_length=256, blank=True)
    sub_domain = models.SlugField(default='', editable=False, max_length=200)

    delivery_fee = models.IntegerField()

    logo = models.ImageField(
        upload_to='shoplogo/', blank=True, null=True)
    banner_image = models.ImageField(
        upload_to='banner/', blank=True, null=True)

    is_active = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop'

    def __str__(self):
        return str(self.name)[:30]

    @property
    def get_logo(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        else:
            # return null
            return ""

    @property
    def get_banner_image(self):
        if self.banner_image and hasattr(self.banner_image, 'url'):
            return self.banner_image.url
        else:
            # return null
            return ""

    def save(self, *args, **kwargs):
        self.sub_domain = (slugify(self.name[:40], allow_unicode=True).strip(
            '-')+'-'+str(uuid.uuid4())[:5]).strip('-')
        super().save(*args, **kwargs)


class ShopCategory(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(default='', editable=False, max_length=200)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shopcategory'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=256)
    price = models.IntegerField()
    description = models.CharField(max_length=256, blank=True)
    slug = models.SlugField(default='', editable=False, max_length=200)

    image = models.ImageField(
        upload_to='shop/', blank=True, null=True)

    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE)

    shopcategory = models.ForeignKey(
        ShopCategory, on_delete=models.CASCADE, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = (slugify(self.name[:40], allow_unicode=True).strip(
            '-')+'-'+str(uuid.uuid4())[:13]).strip('-')
        super().save(*args, **kwargs)


class Order(models.Model):
    # PERCENTAGE SHARING RATIO
    MERCHANT_PERCENTAGE = 97.4
    JUMGA_PERCENTAGE = 2.6

    DRIVER_PERCENTAGE = 80
    JUMGA_DELIVERY_PERCENTAGE = 20

    # FEE FOR DELIVERY
    # DELIVERY_FEE = approximate(20.00)

    # ORDER STATUS
    STANDING = 0
    CANCELLED = 1
    PAYMENT_MADE = 2
    DELIVERED = 3

    CURRENT_STATUS = (
        (STANDING, 'standing'),
        (CANCELLED, 'cancelled'),
        (PAYMENT_MADE, 'paid'),
        (DELIVERED, 'delivered')
    )

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # rider = models.ForeignKey(Rider, on_delete=models.CASCADE)

    address = models.CharField(max_length=250, null=True)
    city = models.CharField(max_length=100, null=True)

    reference_id = models.CharField(max_length=128, blank=True)

    order_items = models.ManyToManyField(
        Product, through='OrderedItem', related_name='orders')

    status = models.IntegerField(choices=CURRENT_STATUS, default=STANDING)

    paid = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_short_name_and_currency(self):
        return {
            "short_name": self.shop.user.country.short_name,
            "currency": self.shop.user.country.currency
        }

    def get_total_cost(self):
        # return sum(item.get_cost() for item in self.items.all())
        subtotal = sum(item.get_cost() for item in self.items.all())
        delivery = self.shop.delivery_fee
        return subtotal + delivery


class OrderedItem(models.Model):
    product = models.ForeignKey(
        Product, related_name='order_items', on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'ordereditem'
        unique_together = (("product", "order"),)

    def __str__(self):
        return self.product.name

    @property
    def get_cost(self):
        return self.quantity * self.item_price


# class Payment(models.Model):

#     NGN = 'NGN'
#     GHS = 'GHS'
#     KES = 'KES'
#     GBP = 'GBP'

#     SHOP_APPROVAL_TOKEN = 'shop_approval'
#     SALE = 'sale'

#     CURRENCY = (
#         (NGN, 'NGN'),
#         (GHS, 'GHS'),
#         (KES, 'KES'),
#         (GBP, 'GBP')
#     )

#     PAYMENT_TYPE = (
#         (SHOP_APPROVAL_TOKEN, 'SHOP_APPROVAL_TOKEN'),
#         (SALE, 'SALE')
#     )

#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     reference = models.CharField(max_length=128)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=5, choices=CURRENCY)
#     payment_type = models.CharField(max_length=64, choices=PAYMENT_TYPE)
#     payment_options = models.CharField(max_length=64)

#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
#     rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
#     jumga = models.ForeignKey(User, on_delete=models.CASCADE)

#     updated_at = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'payment'

#     def __str__(self):
#         return self.order


# class OrderPayment(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     amount = models.BigIntegerField()
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_disbursed = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)
#     # payment_method = models.CharField(max_length=256)

#     class Meta:
#         db_table = 'orderpayment'


# merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
# customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
# rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
# jumga = models.ForeignKey(User, on_delete=models.CASCADE)
