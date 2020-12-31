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
from .serializers import ShopSerializer, ShopCategorySerializer, ProductSerializer
from django.contrib.auth.models import update_last_login
from django.utils import timezone

from jumga.permissions import IsOwnerOrReadOnly
from jumga.access import encoded_reset_token, decode_reset_token
from .models import Shop, ShopCategory, Product

User = get_user_model()

# SHOP VIEWS_____________


class ShopListView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, merchant_id):
        shop = Shop.objects.filter(
            user=merchant_id).order_by('-id')

        if shop:
            serializer = ShopSerializer(shop, many=True)
            return Response(serializer.data)
        else:
            # err = {"error": "not found", "status":404}
            # return response.Response(err, status.HTTP_404_NOT_FOUND)
            err = []
            return response.Response(err, status.HTTP_200_OK)


class ShopNewView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ShopSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(is_active=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopDetailView(APIView):

    def get_object(self, id):
        try:
            return Shop.objects.get(id=id)

        except Shop.DoesNotExist:
            # return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            raise Http404

    def get(self, request, id):
        shop = self.get_object(id)
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def put(self, request, id):
        shop = self.get_object(id)
        serializer = ShopSerializer(shop, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# SHOP CATEGORIES VIEWS____________________

class ShopCategoriesListView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, shop_id):
        shopcategory = ShopCategory.objects.filter(
            shop=shop_id).order_by('-id')

        if shopcategory:
            serializer = ShopCategorySerializer(shopcategory, many=True)
            return Response(serializer.data)
        else:
            # err = {"error": "not found", "status":404}
            # return response.Response(err, status.HTTP_404_NOT_FOUND)
            err = []
            return response.Response(err, status.HTTP_200_OK)


class ShopNewCategoryView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ShopCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopCategoryDetailView(APIView):

    def get_object(self, id):
        try:
            return ShopCategory.objects.get(id=id)

        except ShopCategory.DoesNotExist:
            # return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            raise Http404

    def get(self, request, id):
        shopcategory = self.get_object(id)
        serializer = ShopCategorySerializer(shopcategory)
        return Response(serializer.data)

    def put(self, request, id):
        shopcategory = self.get_object(id)
        serializer = ShopCategorySerializer(shopcategory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# SHOP PRODUCTS VIEWS

class ProductListView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, shop_id):
        product = Product.objects.filter(
            shop=shop_id).order_by('-id')

        if product:
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            # err = {"error": "not found", "status":404}
            # return response.Response(err, status.HTTP_404_NOT_FOUND)
            err = []
            return response.Response(err, status.HTTP_200_OK)


class ProductNewView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)

        except Product.DoesNotExist:
            # return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            raise Http404

    def get(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
