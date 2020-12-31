from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # new
from rest_framework_simplejwt.tokens import RefreshToken
from six import text_type
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Merchant, Customer

User = get_user_model()

# The only reason why this custom login serializer and the view below was created,
# was for the sake of updating last login by the user, else I would have
# used jwt_views.TokenObtainPairView.as_view() in urls.py straight up.


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        print(data)
        return data


class MerchantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Merchant
        fields = ['id', 'first_name', 'last_name', 'phone_number']


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number']


class MerchantSignupSerializer(serializers.ModelSerializer):
    profile = MerchantSerializer(required=True)

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    model = User

    class Meta:
        model = User
        fields = ('password1', 'password2', 'email', 'profile')
        extra_kwargs = {'password1': {'write_only': True},
                        'password2': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password1'],
            is_active=True
        )
        merchant_data = validated_data.pop('profile')
        # create merrchant
        merchant = Merchant.objects.create(
            user=user,
            first_name=merchant_data['first_name'],
            last_name=merchant_data['last_name'],
            phone_number=merchant_data['phone_number'],
        )

        return user

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match.')

        validate_password(data['password1'])
        return data


class CustomerSignupSerializer(serializers.ModelSerializer):
    profile = CustomerSerializer(required=True)

    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    model = User

    class Meta:
        model = User
        fields = ('password1', 'password2', 'email', 'profile')
        extra_kwargs = {'password1': {'write_only': True},
                        'password2': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password1'],
            is_active=True
        )
        customer_data = validated_data.pop('profile')
        # create merrchant
        customer = Customer.objects.create(
            user=user,
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            phone_number=customer_data['phone_number'],
        )

        return user

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match.')

        validate_password(data['password1'])
        return data


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


# class UserProfileSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ['id', 'email', 'username']


# class MerchantSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Merchant
#         fields = ['id', 'first_name', 'last_name', 'phone_number']
