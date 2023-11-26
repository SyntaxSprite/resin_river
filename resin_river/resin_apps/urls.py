from django.urls import path 
from . import views

urlpatterns = [
    path('', views.startingpage, name='index' ),
    path('post/<slug:slug>', views.ItemDetails.as_view(), name='item-details')
]
