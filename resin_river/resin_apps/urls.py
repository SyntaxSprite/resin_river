from django.urls import path 
from . import views

urlpatterns = [
    path('', views.startingpage, name='index' ),
    path('post/<slug:slug>', views.ItemDetails.as_view(), name='item-details'),
    path('add-to-cart', views.AddToCart.as_view(),name='add-to-cart'),
    path('wish-list', views.WishList.as_view(), name='wish-list'),
    path('checkout', views.Checkout.as_view(), name='checkout'),
    path('cart-list', views.CartList.as_view(), name='cart-list'),
    path('sign-up', views.signup, name='sign-up'),
]
