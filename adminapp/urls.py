from django.urls import path,include
from .views import AdminUserView,AdminBlockUser,AdminDashboardView
from adminProductapp.views import AdminProductView,AdminProductAddView,AdminCategoryView,AdminProductEditView,AdminProductDeleteView
from adminOrdersapp.views import AdminOrderView,AdminOrderStausView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('admin-products',AdminProductView,basename='admin-products')

urlpatterns = [
    path('users/',AdminUserView.as_view(),name='adminside-users'),
    path('users/action/<int:pk>/',AdminBlockUser.as_view(),name='user-actions'),
    path('category/action/',AdminCategoryView.as_view(),name='category-actions'),
    path('products/add/',AdminProductAddView.as_view(),name='products-add'),
    path('products/edit/<int:pk>/',AdminProductEditView.as_view(),name='products-edit'),
    path('products/delete/<int:pk>/',AdminProductDeleteView.as_view(),name='products-delete'),
    path('orders/',AdminOrderView.as_view(),name='order-views'),
    path('orders/status/<int:pk>/',AdminOrderStausView.as_view(),name='order-status'),
    path('dashboard/',AdminDashboardView.as_view(),name='admin-dashboard'),
    path('',include(router.urls)),
]