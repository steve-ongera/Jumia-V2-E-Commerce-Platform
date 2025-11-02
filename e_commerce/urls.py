from django.urls import path
from e_commerce import views
# urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('account/', views.account, name='account'),
   
    path('wishlist/', views.wishlist, name='wishlist'),
    path('orders/', views.orders, name='orders'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('phones/', views.phones, name='phones'),
    path('electronics/', views.electronics, name='electronics'),
    path('computing/', views.computing, name='computing'),
    path('fashion/', views.fashion, name='fashion'),
    path('home-kitchen/', views.home_kitchen, name='home'),
    path('health-beauty/', views.health_beauty, name='health'),
    path('sports/', views.sports, name='sports'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),


]