from django.urls import path, re_path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt import views as jwt_views
# from account import views
from jumga.apps.account import views
from jumga.apps.merchant import views as merchant_views


VER_ = 'v1'
account = 'auth'
merchant = 'merchant'
customer = 'customer'
admin = 'admin'

urlpatterns = [
    # account
    path(f'{VER_}/{account}/token/',
         views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f'{VER_}/{account}/refresh/',
         jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path(f'{VER_}/{account}/signup/{merchant}/',
         views.MerchantSignupView.as_view(), name='merchant_signup'),

    path(f'{VER_}/{account}/logout/',
         views.LogoutView.as_view(), name='auth_logout'),
    path(f'{VER_}/{account}/logout_all/',
         views.LogoutAllView.as_view(), name='auth_logout_all'),
    path(f'{VER_}/{account}/password/update/',
         views.UpdatePasswordView.as_view(), name='password_update'),
    path(f'{VER_}/{account}/password_reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset')),

    # /api/auth/password_reset/confirm/
    # /api/auth/password_reset/validate_token/

    path(f'{VER_}/{account}/profile/<uuid:id>',
         views.MerchantProfileView.as_view(), name='profile'),

    # MERCHANT SHOPS
    path(f'{VER_}/{merchant}/profile/<uuid:id>/',
         views.MerchantProfileView.as_view(), name='merchant_profile'),

    path(f'{VER_}/{merchant}/shop/',
         merchant_views.ShopNewView.as_view(), name='merchant_shop_new'),

    path(f'{VER_}/{merchant}/shop/<int:id>/',
         merchant_views.ShopDetailView.as_view(), name='merchant_shop_detail'),

    # *************
    path(f'{VER_}/{merchant}/shops/<uuid:id>/all/',
         merchant_views.ShopListView.as_view(), name='merchant_all_shops'),



    # MERCHANT SHOP CATEGORIES
    path(f'{VER_}/{merchant}/shop/category/',
         merchant_views.ShopNewCategoryView.as_view(), name='merchant_shop_category_new'),

    path(f'{VER_}/{merchant}/shop/category/<int:id>/',
         merchant_views.ShopCategoryDetailView.as_view(), name='merchant_shop_category_detail'),

    path(f'{VER_}/{merchant}/shop/category/<int:shop_id>/all/',
         merchant_views.ShopCategoriesListView.as_view(), name='merchant_all_shop_categories'),


    # MERCHANT SHOP PRODUCTS
    path(f'{VER_}/{merchant}/shop/product/',
         merchant_views.ProductNewView.as_view(), name='merchant_product_new'),

    path(f'{VER_}/{merchant}/shop/product/<int:id>/',
         merchant_views.ProductDetailView.as_view(), name='merchant_product_detail'),

    path(f'{VER_}/{merchant}/shop/products/<int:shop_id>/all/',
         merchant_views.ProductListView.as_view(), name='merchant_all_shop_products'),

    path(f'{VER_}/{merchant}/shop/products/<slug:shop_slug>/all/public/',
         merchant_views.ShopAndProductsView.as_view(), name='all_shop_and_products_public'),

    path(f'{VER_}/{merchant}/payment/',
         merchant_views.PaymentView.as_view(), name='merchant_payment'),

    path(f'{VER_}/{merchant}/order/',
         merchant_views.OrderView.as_view(), name='merchant_order'),

    path(f'{VER_}/{merchant}/allorders/<uuid:id>/',
         merchant_views.MerchantOrdersView.as_view(), name='merchant_all_orders'),

    path(f'{VER_}/{merchant}/overview/<uuid:id>/',
         merchant_views.OverviewView.as_view(), name='overview'),


    path(f'{VER_}/{customer}/orders/<str:email>/<str:contact>/',
         merchant_views.CustomersOrderView.as_view(), name='customer_orders'),

    # Admin
    path(f'{VER_}/{admin}/transactions/',
         merchant_views.TransactionView.as_view(), name='transactions'),

    path(f'{VER_}/{admin}/allorders/',
         merchant_views.AllOrdersView.as_view(), name='all_orders'),

    # OTHERS
    path(f'{VER_}/countries/',
         views.CountryView.as_view(), name='countries'),

]
