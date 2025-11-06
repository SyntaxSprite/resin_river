from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .forms import LoginForm
from .sitemap import ItemsSitemap

sitemaps = {
    'items': ItemsSitemap,
}

urlpatterns = [
    path('', views.startingpage, name='index' ),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('post/<slug:slug>', views.ItemDetails.as_view(), name='item-details'),
    path('add-to-cart', views.AddToCart.as_view(),name='add-to-cart'),
    path('wish-list', views.WishList.as_view(), name='wish-list'),
    path('checkout', views.Checkout.as_view(), name='checkout'),
    path('payment/<int:order_id>', views.Payment.as_view(), name='payment'),
    path('order-confirmation/<int:order_id>', views.OrderConfirmation.as_view(), name='order-confirmation'),
    path('orders/', views.OrderHistory.as_view(), name='order-history'),
    path('orders/<int:order_id>', views.OrderDetail.as_view(), name='order-detail'),
    path('account/', views.UserDashboard.as_view(), name='user-dashboard'),
    path('account/edit/', views.UserProfileEdit.as_view(), name='user-profile-edit'),
    path('account/addresses/', views.SavedAddressesList.as_view(), name='saved-addresses'),
    path('account/addresses/add/', views.SavedAddressAdd.as_view(), name='saved-address-add'),
    path('account/addresses/<int:address_id>/edit/', views.SavedAddressEdit.as_view(), name='saved-address-edit'),
    path('account/addresses/<int:address_id>/delete/', views.SavedAddressDelete.as_view(), name='saved-address-delete'),
    path('cart-list', views.CartList.as_view(), name='cart-list'),
    path('sign-up', views.signup, name='sign-up'),
    path('login/',auth_views.LoginView.as_view(template_name='resin_apps/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name ='logout'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
