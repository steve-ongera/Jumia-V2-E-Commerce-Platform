
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from decimal import Decimal

from .models import (
    Product, Category, Brand, Cart, CartItem, 
    Wishlist, Order, Address, PickupStation, 
    DeliveryZone, Review, Banner
)


def home(request):
    """Homepage view with featured products and banners"""
    
    # Get active banners
    banners = Banner.objects.filter(is_active=True).order_by('order')[:5]
    
    # Featured products
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('brand', 'category', 'vendor')[:12]
    
    # New arrivals
    new_arrivals = Product.objects.filter(
        is_active=True
    ).select_related('brand', 'category', 'vendor').order_by('-created_at')[:12]
    
    # Best sellers
    best_sellers = Product.objects.filter(
        is_active=True
    ).select_related('brand', 'category', 'vendor').order_by('-total_sales')[:12]
    
    # Flash deals (products with compare_price > price)
    flash_deals = Product.objects.filter(
        is_active=True,
        compare_price__gt=0
    ).select_related('brand', 'category', 'vendor')[:12]
    
    # Categories with product count
    categories = Category.objects.filter(
        parent=None, 
        is_active=True
    ).annotate(product_count=Count('products'))[:8]
    
    context = {
        'banners': banners,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'flash_deals': flash_deals,
        'categories': categories,
    }
    
    return render(request, 'e_commerce/home.html', context)


def search(request):
    """Search products"""
    query = request.GET.get('q', '')
    products = Product.objects.none()
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        ).select_related('brand', 'category', 'vendor').distinct()
    
    # Pagination
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'products': page_obj,
        'total_results': products.count(),
    }
    
    return render(request, 'e_commerce/search.html', context)


def category(request, slug):
    """Category detail view with filtering"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all products in this category and subcategories
    categories = [category]
    if category.children.exists():
        categories.extend(list(category.children.filter(is_active=True)))
    
    products = Product.objects.filter(
        category__in=categories,
        is_active=True
    ).select_related('brand', 'category', 'vendor')
    
    # Filtering
    brand_filter = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'default')
    
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-total_sales')
    
    # Get brands for filtering
    brands = Brand.objects.filter(
        products__category__in=categories,
        is_active=True
    ).distinct()
    
    # Pagination
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'brands': brands,
        'subcategories': category.children.filter(is_active=True),
        'total_products': products.count(),
    }
    
    return render(request, 'e_commerce/category.html', context)


def phones(request):
    """Phones & Tablets category"""
    category = get_object_or_404(Category, slug='phones-tablets', is_active=True)
    return category_view(request, category)


def electronics(request):
    """Electronics category"""
    category = get_object_or_404(Category, slug='electronics', is_active=True)
    return category_view(request, category)


def computing(request):
    """Computing category"""
    category = get_object_or_404(Category, slug='computing', is_active=True)
    return category_view(request, category)


def fashion(request):
    """Fashion category"""
    category = get_object_or_404(Category, slug='fashion', is_active=True)
    return category_view(request, category)


def home_kitchen(request):
    """Home & Kitchen category"""
    category = get_object_or_404(Category, slug='home-kitchen', is_active=True)
    return category_view(request, category)


def health_beauty(request):
    """Health & Beauty category"""
    category = get_object_or_404(Category, slug='health-beauty', is_active=True)
    return category_view(request, category)


def sports(request):
    """Sports & Outdoors category"""
    category = get_object_or_404(Category, slug='sports-outdoors', is_active=True)
    return category_view(request, category)


def category_view(request, category):
    """Helper function for category views"""
    categories = [category]
    if category.children.exists():
        categories.extend(list(category.children.filter(is_active=True)))
    
    products = Product.objects.filter(
        category__in=categories,
        is_active=True
    ).select_related('brand', 'category', 'vendor')
    
    # Filtering
    brand_filter = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'default')
    
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-total_sales')
    
    # Get brands for filtering
    brands = Brand.objects.filter(
        products__category__in=categories,
        is_active=True
    ).distinct()
    
    # Pagination
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'brands': brands,
        'subcategories': category.children.filter(is_active=True),
        'total_products': products.count(),
    }
    
    return render(request, 'e_commerce/category.html', context)


@login_required
def account(request):
    """User account dashboard"""
    user = request.user
    
    # Get user's recent orders
    recent_orders = Order.objects.filter(
        user=user
    ).select_related('delivery_address', 'pickup_station').order_by('-created_at')[:5]
    
    # Get user's addresses
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    # Get wishlist count
    wishlist_count = Wishlist.objects.filter(user=user).count()
    
    # Get pending orders count
    pending_orders = Order.objects.filter(
        user=user, 
        status__in=['pending', 'confirmed', 'processing']
    ).count()
    
    context = {
        'recent_orders': recent_orders,
        'addresses': addresses,
        'wishlist_count': wishlist_count,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'e_commerce/account.html', context)


def cart(request):
    """Shopping cart view"""
    cart = None
    cart_items = []
    subtotal = Decimal('0.00')
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    if cart:
        cart_items = cart.items.select_related(
            'product', 
            'product__brand', 
            'product__vendor',
            'variant'
        ).all()
        subtotal = cart.subtotal
    
    # Get delivery zones for delivery fee calculation
    delivery_zones = DeliveryZone.objects.filter(is_active=True).order_by('region', 'city')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_zones': delivery_zones,
    }
    
    return render(request, 'e_commerce/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        variant_id = request.POST.get('variant_id')
        
        # Check stock
        if product.stock < quantity:
            messages.error(request, 'Insufficient stock available.')
            return redirect('product_detail', slug=product.slug)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Get variant if provided
        variant = None
        if variant_id:
            variant = product.variants.filter(id=variant_id, is_active=True).first()
        
        # Check if item already in cart
        cart_item = CartItem.objects.filter(
            cart=cart, 
            product=product, 
            variant=variant
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity in cart.')
        else:
            # Create new cart item
            CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                price=variant.price if variant and variant.price else product.price
            )
            messages.success(request, f'Added {product.name} to cart.')
        
        return redirect('cart')
    
    return redirect('home')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from cart.')
    return redirect('cart')


@login_required
def update_cart(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            # Check stock
            if cart_item.product.stock >= quantity:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully.')
            else:
                messages.error(request, 'Insufficient stock available.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    
    return redirect('cart')


@login_required
def wishlist(request):
    """User wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product', 'product__brand', 'product__category').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(wishlist_items, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'wishlist_items': page_obj,
        'total_items': wishlist_items.count(),
    }
    
    return render(request, 'e_commerce/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'Added {product.name} to wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    # Return to previous page or product detail
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def remove_from_wishlist(request, item_id):
    """Remove item from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'Removed {product_name} from wishlist.')
    return redirect('wishlist')


@login_required
def orders(request):
    """User orders list"""
    user_orders = Order.objects.filter(
        user=request.user
    ).select_related(
        'delivery_address', 
        'pickup_station'
    ).prefetch_related('items', 'payments').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        user_orders = user_orders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(user_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Order status choices for filter
    order_statuses = Order.ORDER_STATUS
    
    context = {
        'orders': page_obj,
        'order_statuses': order_statuses,
        'current_status': status_filter,
        'total_orders': user_orders.count(),
    }
    
    return render(request, 'e_commerce/orders.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail view"""
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        user=request.user
    )
    
    order_items = order.items.select_related('product', 'vendor').all()
    payment = order.payments.first()
    
    context = {
        'order': order,
        'order_items': order_items,
        'payment': payment,
    }
    
    return render(request, 'e_commerce/order_detail.html', context)


def product_detail(request, slug):
    """Product detail view"""
    product = get_object_or_404(
        Product, 
        slug=slug, 
        is_active=True
    )
    
    # Increment views
    product.views += 1
    product.save(update_fields=['views'])
    
    # Get product images
    images = product.images.all().order_by('order')
    
    # Get product variants
    variants = product.variants.filter(is_active=True)
    
    # Get specifications
    specifications = product.specifications.all().order_by('order')
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = reviews.filter(rating=i).count()
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('brand', 'vendor')[:8]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            product=product
        ).exists()
    
    context = {
        'product': product,
        'images': images,
        'variants': variants,
        'specifications': specifications,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    
    return render(request, 'e_commerce/product_detail.html', context)


# AJAX Views for better UX
@login_required
def ajax_add_to_cart(request):
    """AJAX endpoint to add product to cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Insufficient stock available.'
                })
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Added {product.name} to cart.',
                'cart_count': cart.total_items
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def ajax_toggle_wishlist(request):
    """AJAX endpoint to toggle wishlist"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            wishlist_item = Wishlist.objects.filter(
                user=request.user,
                product=product
            ).first()
            
            if wishlist_item:
                wishlist_item.delete()
                return JsonResponse({
                    'success': True,
                    'action': 'removed',
                    'message': f'Removed {product.name} from wishlist.'
                })
            else:
                Wishlist.objects.create(user=request.user, product=product)
                return JsonResponse({
                    'success': True,
                    'action': 'added',
                    'message': f'Added {product.name} to wishlist.'
                })
                
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})