from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal as D
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction, IntegrityError

from jumga.extras import CharNullField
from jumga.apps.account.models import Merchant, Customer, Rider

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
    def country_data(self):
        return self.user.get_country_data

    @property
    def get_banner_image(self):
        if self.banner_image and hasattr(self.banner_image, 'url'):
            return self.banner_image.url
        else:
            # return null
            return ""

    @property
    def rider_full_name(self):
        if self.rider:
            return self.rider.first_name + " " + self.rider.last_name
        return ""


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
        Shop, on_delete=models.CASCADE, related_name="products")

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
    MERCHANT_PERCENTAGE = 0.974
    JUMGA_PERCENTAGE = 0.026

    DRIVER_PERCENTAGE = 0.8
    JUMGA_DELIVERY_PERCENTAGE = 0.2

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
    customer_name = models.CharField(max_length=250, default='')
    customer_email = models.CharField(max_length=250, default='')
    customer_contact = models.CharField(max_length=250, default='')
    # rider = models.ForeignKey(Rider, on_delete=models.CASCADE)

    customer_address = models.CharField(max_length=250, default='')
    customer_city = models.CharField(max_length=100, default='')

    customer_instruction = models.CharField(
        max_length=100, default='', blank=True)

    reference_id = models.CharField(max_length=128, editable=False)

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

    @property
    def get_total_cost(self):
        subtotal = sum([item.get_cost for item in self.items.all()])
        total = self.shop.delivery_fee + subtotal
        return total


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


class Payment(models.Model):

    NGN = 'NGN'
    GHS = 'GHS'
    KES = 'KES'
    GBP = 'GBP'
    USD = 'USD'

    APPROVAL = 'approval'
    SALE = 'sale'

    CURRENCY = (
        (NGN, 'NGN'),
        (GHS, 'GHS'),
        (KES, 'KES'),
        (GBP, 'GBP'),
        (USD, 'USD'),  # For Approval
    )

    PAYMENT_TYPE = (
        (APPROVAL, 'APPROVAL'),
        (SALE, 'SALE')
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCY)

    merchant = models.ForeignKey(
        Merchant, on_delete=models.CASCADE, blank=True, null=True)

    # If shop approval==True
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, blank=True, null=True)

    status = models.CharField(max_length=128)

    flw_ref = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=128)
    tx_ref = models.CharField(max_length=128)

    payment_type = models.CharField(max_length=64, choices=PAYMENT_TYPE)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True)

    narration = models.CharField(max_length=256, default="")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'

    def __str__(self):
        return self.tx_ref


class Transaction(models.Model):
    DEBIT = 'debit'
    CREDIT = 'credit'

    NGN = 'NGN'
    GHS = 'GHS'
    KES = 'KES'
    GBP = 'GBP'
    USD = 'USD'

    TRANSACTION_TYPE = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    )

    CURRENCY = (
        (NGN, 'NGN'),
        (GHS, 'GHS'),
        (KES, 'KES'),
        (GBP, 'GBP'),
        (USD, 'USD'),
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCY)
    beneficiary = models.ForeignKey(User, on_delete=models.CASCADE, )
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE)
    transaction_id = models.CharField(
        default='', max_length=128, editable=False)
    tx_ref_from_payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, blank=True, null=True)

    narration = models.CharField(max_length=256, default="")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return "Transaction ID: "+self.transaction_id

    def save(self, *args, **kwargs):
        self.transaction_id = str(uuid.uuid4())[:18].strip('-')
        super().save(*args, **kwargs)


@receiver(post_save, sender=Payment)
def initiate_transaction(sender, instance, **kwargs):
    jumga_id = 'jumga@gmail.com'

    if kwargs['created']:
        if instance.payment_type == "approval":
            try:
                with transaction.atomic():
                    # 1. Credit Jumga's account
                    # jumga_id = '2e66899b-0ca9-44da-941e-89c949cde8cc'
                    jumga = User.objects.get(
                        email=jumga_id)
                    Transaction.objects.create(
                        beneficiary=jumga,
                        amount=instance.amount,
                        currency=instance.currency,
                        tx_ref_from_payment=instance,
                        narration="Earnings on Shop Approval",
                        transaction_type=Transaction.CREDIT
                    )

                    # 2. Activate shop and Assign Rider
                    # !!! Please, don't this below query in production
                    random_rider = Rider.objects.order_by('?').first()
                    shop_obj = Shop.objects.get(id=instance.shop.id)
                    shop_obj.is_active = True
                    shop_obj.rider = random_rider
                    shop_obj.save()

                    # 3 Credit Account balance of Jumga shop
                    user_obj = User.objects.get(email=jumga_id)
                    user_obj.account_balance += instance.amount
                    user_obj.save()

            except IntegrityError:
                pass

        elif instance.payment_type == "sale":
            try:
                with transaction.atomic():
                    amount = (instance.amount - D(instance.shop.delivery_fee))
                    # 1. Credit Jumga's account on sale
                    Transaction.objects.create(
                        beneficiary_email=jumga_id,
                        amount=amount * D(Order.JUMGA_PERCENTAGE),
                        currency=instance.currency,
                        tx_ref_from_payment=instance,
                        narration="Earnings on Sales",
                        transaction_type=Transaction.CREDIT
                    )
                    # 2. Credit Merchant's account on sale
                    Transaction.objects.create(
                        beneficiary_id=instance.order.shop.user.user.id,
                        amount=amount * D(Order.MERCHANT_PERCENTAGE),
                        currency=instance.currency,
                        tx_ref_from_payment=instance,
                        narration="Earnings on Sales",
                        transaction_type=Transaction.CREDIT
                    )
                    # 3. Credit Jumga's account on Delivery
                    Transaction.objects.create(
                        beneficiary_email=jumga_id,
                        amount=instance.shop.delivery_fee *
                        D(Order.JUMGA_DELIVERY_PERCENTAGE),
                        currency=instance.currency,
                        tx_ref_from_payment=instance,
                        narration="Earnings on Delivery",
                        transaction_type=Transaction.CREDIT
                    )
                    # 4. Credit Rider's account on Delivery
                    Transaction.objects.create(
                        beneficiary_id=instance.order.shop.rider.user.id,
                        amount=instance.shop.delivery_fee *
                        D(Order.DRIVER_PERCENTAGE),
                        currency=instance.currency,
                        tx_ref_from_payment=instance,
                        narration="Earnings on Delivery",
                        transaction_type=Transaction.CREDIT
                    )
                    # 5. Change Order status to paid
                    order_obj = Order.objects.get(id=instance.order.id)
                    order_obj.status = Order.PAYMENT_MADE
                    order_obj.paid = True
                    order_obj.save()

            except IntegrityError:
                pass


@receiver(models.signals.pre_save, sender=Shop)
def detect_if_shop_name_has_changed(sender, instance, **kwargs):
    main_slug = (slugify(instance.name[:40], allow_unicode=True).strip(
        '-')+'-'+str(uuid.uuid4())[:5]).strip('-')

    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field hasn't technically changed, but you may want to do something else here.
        if not instance.sub_domain:
            instance.sub_domain = main_slug
    else:
        if not obj.name == instance.name:  # Field has changed
            instance.sub_domain = main_slug


def set_reference_id(sender, instance, **kwargs):
    if not instance.reference_id:
        instance.reference_id = "ref_"+str(uuid.uuid4())[:14].strip('-')


models.signals.pre_save.connect(set_reference_id, sender=Order)


# merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
# customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
# rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
# jumga = models.ForeignKey(User, on_delete=models.CASCADE)
