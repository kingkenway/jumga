# import deliva.load # Save json city files to db
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Merchant, Customer, Rider
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# from django.conf import settings

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        # (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'email', 'username',
                    'is_active', 'is_staff', 'last_login')
    search_fields = ('email',)
    ordering = ('email',)

    def BE_AWARE_NO_WARNING_clear_tokens_and_delete(self, request, queryset):
        users = queryset.values("id")
        OutstandingToken.objects.filter(user__id__in=users).delete()
        queryset.delete()

    actions = ["BE_AWARE_NO_WARNING_clear_tokens_and_delete"]


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'phone_number',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'phone_number',)


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'phone_number',)
