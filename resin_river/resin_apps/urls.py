from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

urlpatterns = [
    path('', views.startingpage, name='index' ),
    path('post/<slug:slug>', views.ItemDetails.as_view(), name='item-details'),
    path('add-to-cart', views.AddToCart.as_view(),name='add-to-cart'),
    path('wish-list', views.WishList.as_view(), name='wish-list'),
    path('checkout', views.Checkout.as_view(), name='checkout'),
    path('cart-list', views.CartList.as_view(), name='cart-list'),
    path('sign-up', views.signup, name='sign-up'),
    path('login/',auth_views.LoginView.as_view(template_name='resin_apps/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name ='logout')
]
