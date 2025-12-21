from django.urls import path,include
from productsapp.views import ProductView,ProductInduvidualView
from cartapp.views import CartView
from wishlistapp.views import WishlistView
from ordersapp.views import CreateOrderView,DeleteOrderView,RazorpayCreateOrderView,RazorpayVerifyPaymentView,RazorpayCancelOrderView
from rest_framework.routers import  DefaultRouter
from .views import CreateCustomerView, LoginCustomerView, LogoutView,CustomerProfileView,GenerateOTP,VerifyOtp,ResetPassword

router = DefaultRouter()
router.register('products',ProductView,basename='products-view')

urlpatterns = [
    path('',include(router.urls)),
    path('user/register/', CreateCustomerView.as_view(), name='register'),
    path('user/login/', LoginCustomerView.as_view(), name='loginuser'),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('product/<int:id>/',ProductInduvidualView.as_view(),name='induvidual'),
    path('cart/',CartView.as_view(),name='cart'),
    path('cart/<int:product_id>/',CartView.as_view(),name='cart'),
    path('cart/quantity/<int:product_id>/',CartView.as_view(),name='cart-quantity'),
    path('wishlist/',WishlistView.as_view(),name='wishlist'),
    path('wishlist/<int:product_id>/',WishlistView.as_view(),name='wishlist'),
    path('profile/',CustomerProfileView.as_view(),name='profile'),
    path('orders/',CreateOrderView.as_view(),name='place-order'),
    path('razorpay/orders/',RazorpayCreateOrderView.as_view(),name='place-order'),
    path("orders/razorpay/verify/", RazorpayVerifyPaymentView.as_view(), name="razorpay-verify"),
    path("orders/razorpay/cancel/", RazorpayCancelOrderView.as_view(), name="razorpay-cancel-order"),
    path('delete-order/<int:delete_id>/',DeleteOrderView.as_view(),name='delete-order'),
    path('forget-password/',GenerateOTP.as_view(),name='generate-otp'),
    path('verify-otp/',VerifyOtp.as_view(),name='verify-otp'),
    path('reset-password/',ResetPassword.as_view(),name='reset-password'),



]
