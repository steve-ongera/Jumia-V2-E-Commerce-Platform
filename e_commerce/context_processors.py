from e_commerce.models import Category, Cart

def site_context(request):
    # Get all parent categories
    categories = Category.objects.filter(parent=None, is_active=True)
    
    # Get cart item count
    cart_item_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_item_count = cart.total_items
    else:
        # For anonymous users, use session
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
            if cart:
                cart_item_count = cart.total_items
    
    return {
        'categories': categories,
        'cart_item_count': cart_item_count,
    }