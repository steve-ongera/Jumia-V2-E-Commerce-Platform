from django.urls import path
from e_commerce import views
# urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    
    # Main account pages
    path('account/', views.account_overview, name='account_overview'),
    path('orders/', views.account_orders, name='account_orders'),
    path('inbox/', views.account_inbox, name='account_inbox'),
    path('reviews/', views.account_reviews, name='account_reviews'),
    path('wishlist/', views.account_wishlist, name='account_wishlist'),
    path('followed-sellers/', views.account_followed_sellers, name='account_followed_sellers'),
    path('recently-viewed/', views.account_recently_viewed, name='account_recently_viewed'),
    path('settings/', views.account_settings, name='account_settings'),
    path('address-book/', views.account_address_book, name='account_address_book'),
    path('newsletter/', views.account_newsletter, name='account_newsletter'),
    
    # AJAX API endpoints for addresses
    path('api/address/add/', views.api_add_address, name='api_add_address'),
    path('api/address/<int:address_id>/', views.api_get_address, name='api_get_address'),
    path('api/address/<int:address_id>/update/', views.api_update_address, name='api_update_address'),
    path('api/address/<int:address_id>/delete/', views.api_delete_address, name='api_delete_address'),
    path('api/address/<int:address_id>/set-default/', views.api_set_default_address, name='api_set_default_address'),
    
    # AJAX API endpoints for notifications
    path('api/notification/<int:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/read-all/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),

   
    path('wishlist/', views.wishlist, name='wishlist'),
    path('orders/', views.orders, name='orders'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('category-product/<slug:slug>/', views.category_products, name='category_products'),
    path('phones/', views.phones, name='phones'),
    path('electronics/', views.electronics, name='electronics'),
    path('computing/', views.computing, name='computing'),
    path('fashion/', views.fashion, name='fashion'),
    path('home-kitchen/', views.home_kitchen, name='home-kitechen'),
    path('health-beauty/', views.health_beauty, name='health'),
    path('sports/', views.sports, name='sports'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('products/wishlist/<int:product_id>/toggle/' , views.add_to_wishlist , name="add_to_wishlist"),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # AJAX
    path('check-email/', views.check_email_exists, name='check_email'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/update-delivery/', views.update_delivery_method, name='update_delivery_method'),
    path('checkout/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/place-order/', views.place_order, name='place_order'),

    # Payment
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment/mpesa/initiate/<int:payment_id>/', views.initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('payment/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment/status/<int:payment_id>/', views.check_payment_status, name='check_payment_status'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/<int:order_id>/', views.payment_failed, name='payment_failed'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('orders/<int:order_id>/track/', views.track_order, name='track_order'),

]