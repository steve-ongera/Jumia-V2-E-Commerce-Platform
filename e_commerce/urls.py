from django.urls import path
from e_commerce import views
# urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('account/', views.account, name='account'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('orders/', views.orders, name='orders'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('phones/', views.phones, name='phones'),
    path('electronics/', views.electronics, name='electronics'),
    path('computing/', views.computing, name='computing'),
    path('fashion/', views.fashion, name='fashion'),
    path('home-kitchen/', views.home_kitchen, name='home'),
    path('health-beauty/', views.health_beauty, name='health'),
    path('sports/', views.sports, name='sports'),

]