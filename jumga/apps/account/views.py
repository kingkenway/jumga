from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, response, decorators
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from django.core.mail import send_mail
# from .serializers import UserTokenObtainPairSerializer, UserSerializer, UserProfileSerializer, UserChangePasswordSerializer, RestaurantProfileSerializer, DriverProfileSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login
from django.utils import timezone

from jumga.permissions import IsOwnerOrReadOnly
from jumga.access import encoded_reset_token, decode_reset_token
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .serializers import UserTokenObtainPairSerializer, MerchantSignupSerializer, MerchantSerializer, UserChangePasswordSerializer, CountrySerializer, MerchantProfileSerializer
from .models import Merchant, Country


User = get_user_model()


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


# Ordinarily, the commented view above is to be used,
# but due to an admin been given a 201 status even though
# its cred. are invalid. THis below is just an hack tho.
# Not really necessary
# class TokenObtainPairView(TokenObtainPairView):

#     def post(self, request):
#         serializer = UserTokenObtainPairSerializer(data=request.data)

#         if serializer.is_valid(self):
#             error = {'detail': 'No active account found with the given credentials'}
#             return response.Response(error, status.HTTP_401_UNAUTHORIZED)


class MerchantSignupView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MerchantSignupSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.data['email'])
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            user_data = {}
            user_data['id'] = user.id
            user_data['email'] = user.email
            user_data['merchant_id'] = user.merchant.id
            user_data['first_name'] = user.merchant.first_name
            user_data['last_name'] = user.merchant.last_name
            user_data['country'] = user.merchant.get_country_data
            user_data['phone_number'] = user.merchant.phone_number

            data = {
                "status": 201,
                "message": "user created",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "profile": user_data
            }

            return response.Response(data, status.HTTP_201_CREATED)
            # return response.Response({"status": 201, "message": "user created"}, status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MerchantProfileView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, id):
        try:
            user = User.objects.get(id=id)
            self.check_object_permissions(self.request, user)
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self, request, id):
        # token = request.headers.get('Authorization')
        user = self.get_object(id)
        serializer = MerchantProfileSerializer(user)
        # data = serializer.data
        data = {
            "message": "ok",
            "data": serializer.data
        }
        return Response(data)

    def put(self, request, id,  format=None):
        profile = self.get_object(id)

        serializer = MerchantProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RestaurantProfileView(APIView):
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

#     def get_object(self, id):
#         try:
#             user = Restaurant.objects.get(user_id=id)
#             self.check_object_permissions(self.request, user)
#             return user
#         except Restaurant.DoesNotExist:
#             raise Http404

#     def get(self, request, id):
#         # token = request.headers.get('Authorization')
#         user = self.get_object(id)
#         serializer = RestaurantProfileSerializer(user)
#         # data = serializer.data
#         data = {
#             "message": "ok",
#             "data": serializer.data
#         }
#         return Response(data)

#         # serializer = UserProfileSerializer(data=request.data)
#         # if serializer.is_valid():
#         #     serializer.save()
#         #     return response.Response( {"status": 201}, status.HTTP_201_CREATED)
#         # return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

#     def put(self, request, id,  format=None):
#         profile = self.get_object(id)

#         serializer = RestaurantProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, queryset=None):
        self.check_object_permissions(self.request, self.request.user)
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = UserChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class CountryView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


# Generate new fernet key
# key = Fernet.generate_key()
# https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
