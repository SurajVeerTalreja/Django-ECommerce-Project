from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrement_cart/<int:product_id>/<int:cart_item_id>/', views.decrement_cart, name='decrement_cart'),
    path('delete_cart/<int:product_id>/<int:cart_item_id>/', views.delete_cart, name='delete_cart'),
    path('checkout/', views.checkout, name='checkout'),
]