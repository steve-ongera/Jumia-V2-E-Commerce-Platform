
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

from django.shortcuts import render
from django.db.models import Q, Count, Avg
from .models import (
    Product, Category, Banner, Brand, 
    Vendor, Review, DeliveryZone
)
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import User
import json


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password')
            return render(request, 'auth/login.html')
        
        # Authenticate user
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect to next page or home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([first_name, last_name, email, phone_number, password]):
            messages.error(request, 'All fields are required')
            return render(request, 'auth/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'auth/register.html')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'auth/register.html')
        
        # Check if phone exists
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered')
            return render(request, 'auth/register.html')
        
        try:
            # Create user
            username = email.split('@')[0] + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
            
            # Auto login after registration
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Jumia.')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


def forgot_password_view(request):
    """Forgot password view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please provide your email address')
            return render(request, 'auth/forgot_password.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            reset_link = request.build_absolute_uri(
                f'/auth/reset-password/{uid}/{token}/'
            )
            
            # Send email
            subject = 'Reset Your Jumia Password'
            message = render_to_string('auth/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email')
            return redirect('login')
            
        except User.DoesNotExist:
            # Don't reveal that email doesn't exist for security
            messages.success(request, 'If that email exists, a password reset link has been sent')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Error sending reset email. Please try again later.')
    
    return render(request, 'auth/forgot_password.html')


def reset_password_view(request, uidb64, token):
    """Reset password view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not password or not confirm_password:
                messages.error(request, 'Please provide both password fields')
                return render(request, 'auth/reset_password.html')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return render(request, 'auth/reset_password.html')
            
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long')
                return render(request, 'auth/reset_password.html')
            
            # Set new password
            user.set_password(password)
            user.save()
            
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('login')
        
        return render(request, 'auth/reset_password.html', {'valid_link': True})
    else:
        messages.error(request, 'Invalid or expired reset link')
        return redirect('forgot_password')


@login_required
def change_password_view(request):
    """Change password for logged in user"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not all([old_password, new_password, confirm_password]):
            messages.error(request, 'All fields are required')
            return render(request, 'auth/change_password.html')
        
        # Check old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect')
            return render(request, 'auth/change_password.html')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return render(request, 'auth/change_password.html')
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'auth/change_password.html')
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Keep user logged in after password change
        login(request, request.user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('account')
    
    return render(request, 'auth/change_password.html')


def check_email_exists(request):
    """AJAX endpoint to check if email exists"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def home(request):
    """Home page view with Jumia-style layout"""
    
    # Active banners for hero slider
    banners = Banner.objects.filter(
        is_active=True
    ).filter(
        Q(start_date__lte=datetime.now()) | Q(start_date__isnull=True)
    ).filter(
        Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True)
    )[:5]
    
    # Main categories for sidebar
    main_categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('children')[:12]
    
    # Flash Sales - products with discount
    flash_sales = Product.objects.filter(
        is_active=True,
        stock__gt=0,
        compare_price__gt=0
    ).exclude(
        compare_price=0
    ).order_by('-total_sales')[:12]
    
    # Top Deals - featured products
    top_deals = Product.objects.filter(
        is_active=True,
        is_featured=True,
        stock__gt=0
    ).order_by('-total_sales', '-views')[:20]
    
    # Best Sellers
    best_sellers = Product.objects.filter(
        is_active=True,
        stock__gt=0
    ).order_by('-total_sales')[:12]
    
    # New Arrivals - products from last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_arrivals = Product.objects.filter(
        is_active=True,
        stock__gt=0,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:12]
    
    # Electronics category
    electronics = None
    electronics_products = []
    try:
        electronics = Category.objects.get(slug='electronics', is_active=True)
        electronics_products = Product.objects.filter(
            category__in=[electronics] + list(electronics.children.all()),
            is_active=True,
            stock__gt=0
        ).order_by('-total_sales')[:12]
    except Category.DoesNotExist:
        pass
    
    # Fashion category
    fashion = None
    fashion_products = []
    try:
        fashion = Category.objects.get(slug='fashion', is_active=True)
        fashion_products = Product.objects.filter(
            category__in=[fashion] + list(fashion.children.all()),
            is_active=True,
            stock__gt=0
        ).order_by('-total_sales')[:12]
    except Category.DoesNotExist:
        pass
    
    # Home & Kitchen category
    home_kitchen = None
    home_kitchen_products = []
    try:
        home_kitchen = Category.objects.get(slug='home-kitchen', is_active=True)
        home_kitchen_products = Product.objects.filter(
            category__in=[home_kitchen] + list(home_kitchen.children.all()),
            is_active=True,
            stock__gt=0
        ).order_by('-total_sales')[:12]
    except Category.DoesNotExist:
        pass
    
    # Phones & Tablets category
    phones_tablets = None
    phones_products = []
    try:
        phones_tablets = Category.objects.get(slug='phones-tablets', is_active=True)
        phones_products = Product.objects.filter(
            category__in=[phones_tablets] + list(phones_tablets.children.all()),
            is_active=True,
            stock__gt=0
        ).order_by('-total_sales')[:12]
    except Category.DoesNotExist:
        pass
    
    # Top brands
    top_brands = Brand.objects.filter(
        is_active=True,
        products__is_active=True
    ).annotate(
        product_count=Count('products')
    ).filter(
        product_count__gt=0
    ).order_by('-product_count')[:12]
    
    # Top vendors
    top_vendors = Vendor.objects.filter(
        is_active=True,
        is_verified=True
    ).order_by('-rating')[:8]
    
    context = {
        'banners': banners,
        'main_categories': main_categories,
        'flash_sales': flash_sales,
        'top_deals': top_deals,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'electronics': electronics,
        'electronics_products': electronics_products,
        'fashion': fashion,
        'fashion_products': fashion_products,
        'home_kitchen': home_kitchen,
        'home_kitchen_products': home_kitchen_products,
        'phones_tablets': phones_tablets,
        'phones_products': phones_products,
        'top_brands': top_brands,
        'top_vendors': top_vendors,
    }
    
    return render(request, 'home.html', context)


from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, Avg, Count
from .models import Category, Product, Brand, ProductSpecification
from decimal import Decimal


def category_products(request, slug):
    """Category products listing with filters"""
    
    # Get category
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all subcategories
    subcategories = category.children.filter(is_active=True)
    
    # Get all categories in this hierarchy (parent + children)
    category_ids = [category.id] + list(subcategories.values_list('id', flat=True))
    
    # Base queryset
    products = Product.objects.filter(
        category_id__in=category_ids,
        is_active=True,
        stock__gt=0
    ).select_related('brand', 'category', 'vendor').prefetch_related('images', 'reviews')
    
    # Get filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    brand_ids = request.GET.getlist('brand')
    subcategory_ids = request.GET.getlist('subcategory')
    rating = request.GET.get('rating')
    sort_by = request.GET.get('sort', 'popular')
    
    # Apply filters
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except:
            pass
    
    if brand_ids:
        products = products.filter(brand_id__in=brand_ids)
    
    if subcategory_ids:
        products = products.filter(category_id__in=subcategory_ids)
    
    if rating:
        try:
            rating_value = int(rating)
            # Filter products with average rating >= rating_value
            products = products.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=rating_value)
        except:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')
    else:  # popular (default)
        products = products.order_by('-total_sales', '-views')
    
    # Get price range for all products in category (for filter slider)
    price_range = Product.objects.filter(
        category_id__in=category_ids,
        is_active=True,
        stock__gt=0
    ).aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get brands available in this category
    brands = Brand.objects.filter(
        products__category_id__in=category_ids,
        products__is_active=True,
        products__stock__gt=0,
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(
            products__category_id__in=category_ids,
            products__is_active=True,
            products__stock__gt=0
        ))
    ).filter(product_count__gt=0).order_by('name')
    
    # Get common specifications for filtering
    specifications = ProductSpecification.objects.filter(
        product__category_id__in=category_ids,
        product__is_active=True
    ).values('name').annotate(
        count=Count('id')
    ).filter(count__gte=5).order_by('name')[:10]
    
    # Get specification values for each spec
    spec_filters = {}
    for spec in specifications:
        spec_name = spec['name']
        spec_values = ProductSpecification.objects.filter(
            product__category_id__in=category_ids,
            product__is_active=True,
            name=spec_name
        ).values('value').annotate(
            count=Count('id')
        ).order_by('value')[:20]
        
        if spec_values:
            spec_filters[spec_name] = spec_values
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products, 40)  # 40 products per page
    page_obj = paginator.get_page(page_number)
    
    # Build context
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': page_obj,
        'page_obj': page_obj,
        'brands': brands,
        'price_range': price_range,
        'spec_filters': spec_filters,
        'total_products': products.count(),
        
        # Current filters
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
        'current_brands': [int(b) for b in brand_ids] if brand_ids else [],
        'current_subcategories': [int(s) for s in subcategory_ids] if subcategory_ids else [],
        'current_rating': rating or '',
        'current_sort': sort_by,
    }
    
    return render(request, 'category_products.html', context)

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
    
    return render(request, 'wishlist.html', context)

from django.views.decorators.http import require_POST
@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Toggle product in wishlist - AJAX endpoint"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if item already exists
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if wishlist_item:
            # Remove from wishlist
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'in_wishlist': False,
                'message': f'{product.name} removed from wishlist'
            })
        else:
            # Add to wishlist
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            return JsonResponse({
                'success': True,
                'in_wishlist': True,
                'message': f'{product.name} added to wishlist'
            })
            
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from .models import (
    Product, ProductImage, ProductVariant, 
    ProductSpecification, Review, Cart, 
    CartItem, Wishlist, Category
)
import json


def product_detail(request, slug):
    """Product detail page with all information"""
    
    # Get product
    product = get_object_or_404(
        Product.objects.select_related('vendor', 'category', 'brand')
        .prefetch_related('images', 'variants', 'specifications', 'reviews__user'),
        slug=slug,
        is_active=True
    )
    
    # Increment view count
    product.views += 1
    product.save(update_fields=['views'])
    
    # Get product images
    images = product.images.all().order_by('order', 'id')
    primary_image = images.filter(is_primary=True).first() or images.first()
    
    # Get variants
    variants = product.variants.filter(is_active=True)
    
    # Get specifications grouped
    specifications = product.specifications.all().order_by('order')
    
    # Get reviews with statistics
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Review statistics
    review_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id'),
        five_star=Count('id', filter=Q(rating=5)),
        four_star=Count('id', filter=Q(rating=4)),
        three_star=Count('id', filter=Q(rating=3)),
        two_star=Count('id', filter=Q(rating=2)),
        one_star=Count('id', filter=Q(rating=1)),
    )
    
    # Calculate rating percentages
    total_reviews = review_stats['total_reviews'] or 1
    rating_distribution = {
        5: (review_stats['five_star'] / total_reviews) * 100,
        4: (review_stats['four_star'] / total_reviews) * 100,
        3: (review_stats['three_star'] / total_reviews) * 100,
        2: (review_stats['two_star'] / total_reviews) * 100,
        1: (review_stats['one_star'] / total_reviews) * 100,
    }
    
    # Check if user has purchased this product
    has_purchased = False
    user_review = None
    if request.user.is_authenticated:
        has_purchased = product.orderitem_set.filter(
            order__user=request.user,
            order__status='delivered'
        ).exists()
        
        # Check if user already reviewed
        user_review = reviews.filter(user=request.user).first()
    
    # Related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock__gt=0
    ).exclude(id=product.id).order_by('-total_sales')[:12]
    
    # You may also like (from same vendor)
    vendor_products = Product.objects.filter(
        vendor=product.vendor,
        is_active=True,
        stock__gt=0
    ).exclude(id=product.id).order_by('-total_sales')[:6]
    
    # Recently viewed products (from session)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if product.id in recently_viewed_ids:
        recently_viewed_ids.remove(product.id)
    recently_viewed_ids.insert(0, product.id)
    request.session['recently_viewed'] = recently_viewed_ids[:10]
    
    recently_viewed = Product.objects.filter(
        id__in=recently_viewed_ids,
        is_active=True
    ).exclude(id=product.id)[:6]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    # Breadcrumb categories
    breadcrumb_categories = []
    current_category = product.category
    while current_category:
        breadcrumb_categories.insert(0, current_category)
        current_category = current_category.parent
    
    context = {
        'product': product,
        'images': images,
        'primary_image': primary_image,
        'variants': variants,
        'specifications': specifications,
        'reviews': reviews[:10],  # First 10 reviews
        'review_stats': review_stats,
        'rating_distribution': rating_distribution,
        'has_purchased': has_purchased,
        'user_review': user_review,
        'related_products': related_products,
        'vendor_products': vendor_products,
        'recently_viewed': recently_viewed,
        'in_wishlist': in_wishlist,
        'breadcrumb_categories': breadcrumb_categories,
    }
    
    return render(request, 'product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if variant is selected
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        
        # Check stock
        available_stock = variant.stock if variant else product.stock
        if quantity > available_stock:
            messages.error(request, 'Not enough stock available.')
            return redirect('product_detail', slug=product.slug)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity, 'price': variant.price if variant else product.price}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            if cart_item.quantity > available_stock:
                cart_item.quantity = available_stock
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('cart')
    
    return redirect('home')


@login_required
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        in_wishlist = False
        message = 'Removed from wishlist'
    else:
        Wishlist.objects.create(user=request.user, product=product)
        in_wishlist = True
        message = 'Added to wishlist'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'in_wishlist': in_wishlist, 'message': message})
    
    messages.success(request, message)
    return redirect('product_detail', slug=product.slug)


@login_required
def submit_review(request, product_id):
    """Submit product review"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if user has purchased
        has_purchased = product.orderitem_set.filter(
            order__user=request.user,
            order__status='delivered'
        ).exists()
        
        if not has_purchased:
            messages.error(request, 'You can only review products you have purchased.')
            return redirect('product_detail', slug=product.slug)
        
        # Check if user already reviewed
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            messages.error(request, 'You have already reviewed this product.')
            return redirect('product_detail', slug=product.slug)
        
        # Create review
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=True,
            is_approved=False  # Requires admin approval
        )
        
        messages.success(request, 'Your review has been submitted and is pending approval.')
        return redirect('product_detail', slug=product.slug)
    
    return redirect('home')

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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Cart, CartItem, Product, ProductVariant
from decimal import Decimal
import json


@login_required
def cart_view(request):
    """Shopping cart page"""
    
    # Get or create cart for user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get cart items with related data
    cart_items = cart.items.select_related(
        'product__brand',
        'product__vendor',
        'product__category',
        'variant'
    ).prefetch_related(
        'product__images'
    ).all()
    
    # Calculate totals
    subtotal = cart.subtotal
    
    
    # Total
    total = subtotal 
    
    # Get recently viewed products (from session or cookie)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(
        id__in=recently_viewed_ids,
        is_active=True,
        stock__gt=0
    ).prefetch_related('images')[:8]
    
    # Get recommended products based on cart items
    if cart_items.exists():
        # Get categories from cart items
        cart_categories = [item.product.category_id for item in cart_items if item.product.category]
        
        # Get similar products
        similar_products = Product.objects.filter(
            category_id__in=cart_categories,
            is_active=True,
            stock__gt=0
        ).exclude(
            id__in=[item.product_id for item in cart_items]
        ).order_by('-total_sales')[:8]
    else:
        # Show popular products if cart is empty
        similar_products = Product.objects.filter(
            is_active=True,
            stock__gt=0
        ).order_by('-total_sales')[:8]
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'recently_viewed': recently_viewed,
        'similar_products': similar_products,
    }
    
    return render(request, 'cart.html', context)


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(
                CartItem,
                id=item_id,
                cart__user=request.user
            )
            
            action = request.POST.get('action')
            
            if action == 'increase':
                # Check stock availability
                if cart_item.product.stock > cart_item.quantity:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    return JsonResponse({
                        'error': 'Maximum stock reached'
                    }, status=400)
            
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    return JsonResponse({
                        'error': 'Minimum quantity is 1'
                    }, status=400)
            
            elif action == 'update':
                quantity = int(request.POST.get('quantity', 1))
                
                if quantity < 1:
                    return JsonResponse({
                        'error': 'Minimum quantity is 1'
                    }, status=400)
                
                if quantity > cart_item.product.stock:
                    return JsonResponse({
                        'error': 'Insufficient stock'
                    }, status=400)
                
                cart_item.quantity = quantity
                cart_item.save()
            
            # Recalculate totals
            cart = cart_item.cart
            item_total = cart_item.total_price
            cart_subtotal = cart.subtotal
            delivery_fee = Decimal('200.00')
            cart_total = cart_subtotal + delivery_fee
            
            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity,
                'item_total': float(item_total),
                'cart_subtotal': float(cart_subtotal),
                'cart_total': float(cart_total),
                'total_items': cart.total_items
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(
                CartItem,
                id=item_id,
                cart__user=request.user
            )
            
            cart = cart_item.cart
            cart_item.delete()
            
            # Recalculate totals
            cart_subtotal = cart.subtotal
            delivery_fee = Decimal('200.00') if cart.items.exists() else Decimal('0.00')
            cart_total = cart_subtotal + delivery_fee
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'cart_subtotal': float(cart_subtotal),
                'cart_total': float(cart_total),
                'total_items': cart.total_items,
                'cart_empty': not cart.items.exists()
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            
            messages.success(request, 'Cart cleared successfully')
            return redirect('cart')
            
        except Cart.DoesNotExist:
            messages.error(request, 'Cart not found')
            return redirect('cart')
    
    return redirect('cart')


def add_to_cart(request, product_id):
    """Add product to cart (updated version)"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'Please login to add items to cart',
            'redirect': '/login/'
        }, status=401)
    
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id, is_active=True)
            quantity = int(request.POST.get('quantity', 1))
            variant_id = request.POST.get('variant_id')
            
            # Validate quantity
            if quantity < 1:
                return JsonResponse({'error': 'Invalid quantity'}, status=400)
            
            # Check stock
            if product.stock < quantity:
                return JsonResponse({'error': 'Insufficient stock'}, status=400)
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Get variant if specified
            variant = None
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
                if variant.stock < quantity:
                    return JsonResponse({'error': 'Insufficient variant stock'}, status=400)
            
            # Check if item already in cart
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=product,
                variant=variant
            ).first()
            
            if cart_item:
                # Update quantity
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return JsonResponse({'error': 'Insufficient stock'}, status=400)
                cart_item.quantity = new_quantity
                cart_item.save()
            else:
                # Create new cart item
                price = variant.price if variant and variant.price else product.price
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    price=price
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart',
                'cart_count': cart.total_items
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import (
    Cart, Order, OrderItem, Payment, Address, 
    PickupStation, DeliveryZone, Coupon
)
from decimal import Decimal
import json


@login_required
def checkout(request):
    """Checkout page"""
    
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related(
            'product__vendor',
            'product__brand',
            'variant'
        ).prefetch_related('product__images').all()
        
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty')
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Get user's addresses
    addresses = request.user.addresses.all().order_by('-is_default', '-created_at')
    default_address = addresses.filter(is_default=True).first() or addresses.first()
    
    # Get active pickup stations
    pickup_stations = PickupStation.objects.filter(is_active=True).order_by('city', 'name')
    
    # Get delivery zones for pricing
    delivery_zones = DeliveryZone.objects.filter(is_active=True)
    
    # Calculate subtotal
    subtotal = cart.subtotal
    
    # Default delivery method and fee
    delivery_method = request.session.get('delivery_method', 'pickup_station')
    
    # Calculate delivery fee based on method
    if delivery_method == 'home_delivery' and default_address:
        # Get delivery fee for user's location
        delivery_zone = delivery_zones.filter(
            region=default_address.region,
            city=default_address.city
        ).first()
        delivery_fee = delivery_zone.delivery_fee if delivery_zone else Decimal('300.00')
    else:
        # Pickup station default fee
        delivery_fee = Decimal('0.00')
    
    # Get applied coupon from session
    coupon_code = request.session.get('coupon_code')
    discount = Decimal('0.00')
    coupon = None
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            
            # Check minimum purchase
            if subtotal >= coupon.minimum_purchase:
                if coupon.discount_type == 'percentage':
                    discount = (subtotal * coupon.discount_value) / 100
                    if coupon.maximum_discount:
                        discount = min(discount, coupon.maximum_discount)
                else:
                    discount = coupon.discount_value
            else:
                messages.warning(request, f'Minimum purchase of KSh {coupon.minimum_purchase} required for this coupon')
                del request.session['coupon_code']
                
        except Coupon.DoesNotExist:
            del request.session['coupon_code']
    
    # Calculate total
    total = subtotal + delivery_fee - discount
    
    # Group cart items by vendor for shipment display
    shipments = {}
    for item in cart_items:
        vendor_id = item.product.vendor_id
        if vendor_id not in shipments:
            shipments[vendor_id] = {
                'vendor': item.product.vendor,
                'items': []
            }
        shipments[vendor_id]['items'].append(item)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'pickup_stations': pickup_stations,
        'delivery_zones': delivery_zones,
        'shipments': shipments.values(),
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'discount': discount,
        'total': total,
        'delivery_method': delivery_method,
        'coupon': coupon,
    }
    
    return render(request, 'checkout.html', context)


@login_required
def update_delivery_method(request):
    """Update delivery method and recalculate fees via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            delivery_method = data.get('delivery_method')
            station_id = data.get('station_id')
            address_id = data.get('address_id')
            
            # Save to session
            request.session['delivery_method'] = delivery_method
            
            # Get cart
            cart = Cart.objects.get(user=request.user)
            subtotal = cart.subtotal
            
            # Calculate delivery fee
            if delivery_method == 'pickup_station':
                if station_id:
                    station = get_object_or_404(PickupStation, id=station_id, is_active=True)
                    request.session['pickup_station_id'] = station_id
                    # Use station-specific fee if available, otherwise default
                    delivery_fee = getattr(station, 'delivery_fee', Decimal('150.00'))
                else:
                    delivery_fee = Decimal('150.00')
            else:  # home_delivery
                if address_id:
                    address = get_object_or_404(Address, id=address_id, user=request.user)
                    request.session['delivery_address_id'] = address_id
                    
                    # Get delivery zone for address
                    delivery_zone = DeliveryZone.objects.filter(
                        region=address.region,
                        city=address.city,
                        is_active=True
                    ).first()
                    
                    delivery_fee = delivery_zone.delivery_fee if delivery_zone else Decimal('300.00')
                else:
                    delivery_fee = Decimal('300.00')
            
            # Get discount from session
            discount = Decimal('0.00')
            coupon_code = request.session.get('coupon_code')
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(
                        code=coupon_code,
                        is_active=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now()
                    )
                    if subtotal >= coupon.minimum_purchase:
                        if coupon.discount_type == 'percentage':
                            discount = (subtotal * coupon.discount_value) / 100
                            if coupon.maximum_discount:
                                discount = min(discount, coupon.maximum_discount)
                        else:
                            discount = coupon.discount_value
                except Coupon.DoesNotExist:
                    pass
            
            # Calculate total
            total = subtotal + delivery_fee - discount
            
            return JsonResponse({
                'success': True,
                'subtotal': float(subtotal),
                'delivery_fee': float(delivery_fee),
                'discount': float(discount),
                'total': float(total)
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def apply_coupon(request):
    """Apply coupon code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip().upper()
            
            if not code:
                return JsonResponse({
                    'error': 'Please enter a coupon code'
                }, status=400)
            
            # Get cart
            cart = Cart.objects.get(user=request.user)
            subtotal = cart.subtotal
            
            # Validate coupon
            try:
                coupon = Coupon.objects.get(
                    code=code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'error': 'Invalid or expired coupon code'
                }, status=400)
            
            # Check usage limits
            if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                return JsonResponse({
                    'error': 'This coupon has reached its usage limit'
                }, status=400)
            
            # Check user usage
            user_usage = Order.objects.filter(
                user=request.user,
                customer_note__contains=code
            ).count()
            
            if user_usage >= coupon.user_limit:
                return JsonResponse({
                    'error': 'You have already used this coupon'
                }, status=400)
            
            # Check minimum purchase
            if subtotal < coupon.minimum_purchase:
                return JsonResponse({
                    'error': f'Minimum purchase of KSh {coupon.minimum_purchase} required'
                }, status=400)
            
            # Calculate discount
            if coupon.discount_type == 'percentage':
                discount = (subtotal * coupon.discount_value) / 100
                if coupon.maximum_discount:
                    discount = min(discount, coupon.maximum_discount)
            else:
                discount = coupon.discount_value
            
            # Save to session
            request.session['coupon_code'] = code
            
            # Recalculate total
            delivery_method = request.session.get('delivery_method', 'pickup_station')
            delivery_fee = Decimal('150.00') if delivery_method == 'pickup_station' else Decimal('300.00')
            total = subtotal + delivery_fee - discount
            
            return JsonResponse({
                'success': True,
                'message': 'Coupon applied successfully',
                'discount': float(discount),
                'total': float(total)
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from .models import Order, Payment
import requests
import base64
import json
from datetime import datetime


@login_required
def payment_page(request, order_id):
    """Payment page for order"""
    
    order = get_object_or_404(
        Order.objects.select_related(
            'user',
            'delivery_address',
            'pickup_station'
        ).prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )
    
    # Get or create payment
    payment = order.payments.first()
    if not payment:
        payment = Payment.objects.create(
            order=order,
            payment_method='mpesa',
            amount=order.total,
            status='pending'
        )
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payment.html', context)


@login_required
def initiate_mpesa_payment(request, payment_id):
    """Initiate M-Pesa STK Push"""
    if request.method == 'POST':
        try:
            payment = get_object_or_404(
                Payment.objects.select_related('order'),
                id=payment_id,
                order__user=request.user
            )
            
            if payment.status == 'completed':
                return JsonResponse({
                    'error': 'Payment already completed'
                }, status=400)
            
            # Get phone number from request
            phone_number = request.POST.get('phone_number', '').strip()
            
            if not phone_number:
                return JsonResponse({
                    'error': 'Phone number is required'
                }, status=400)
            
            # Format phone number (remove + and spaces, ensure starts with 254)
            phone_number = phone_number.replace('+', '').replace(' ', '')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Validate phone number
            if not phone_number.isdigit() or len(phone_number) != 12:
                return JsonResponse({
                    'error': 'Invalid phone number format. Use 07XXXXXXXX or 2547XXXXXXXX'
                }, status=400)
            
            # Get M-Pesa access token
            access_token = get_mpesa_access_token()
            
            if not access_token:
                return JsonResponse({
                    'error': 'Failed to authenticate with M-Pesa'
                }, status=500)
            
            # Prepare STK Push request
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            business_short_code = settings.MPESA_SHORTCODE
            passkey = settings.MPESA_PASSKEY
            
            # Generate password
            password = base64.b64encode(
                (business_short_code + passkey + timestamp).encode()
            ).decode('utf-8')
            
            # Prepare request payload
            stk_push_url = settings.MPESA_STK_PUSH_URL
            callback_url = settings.MPESA_CALLBACK_URL
            
            payload = {
                "BusinessShortCode": business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(payment.amount),
                "PartyA": phone_number,
                "PartyB": business_short_code,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": payment.order.order_number,
                "TransactionDesc": f"Payment for Order {payment.order.order_number}"
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make STK Push request
            response = requests.post(stk_push_url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ResponseCode') == '0':
                # Update payment with checkout request ID
                payment.status = 'processing'
                payment.mpesa_phone = phone_number
                payment.response_data = response_data
                payment.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Payment request sent. Please check your phone.',
                    'checkout_request_id': response_data.get('CheckoutRequestID')
                })
            else:
                # Log error
                error_message = response_data.get('errorMessage', 'Failed to initiate payment')
                payment.status = 'failed'
                payment.failure_reason = error_message
                payment.response_data = response_data
                payment.save()
                
                return JsonResponse({
                    'error': error_message
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_mpesa_access_token():
    """Get M-Pesa OAuth access token"""
    try:
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        auth_url = settings.MPESA_AUTH_URL
        
        # Encode credentials
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {credentials}"
        }
        
        response = requests.get(auth_url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        return None
        
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


@login_required
def check_payment_status(request, payment_id):
    """Check M-Pesa payment status"""
    try:
        payment = get_object_or_404(
            Payment.objects.select_related('order'),
            id=payment_id,
            order__user=request.user
        )
        
        return JsonResponse({
            'status': payment.status,
            'payment_method': payment.payment_method,
            'amount': float(payment.amount),
            'transaction_id': payment.transaction_id,
            'mpesa_receipt': payment.mpesa_receipt,
            'order_number': payment.order.order_number,
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)


@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback endpoint"""
    try:
        # Get callback data
        callback_data = json.loads(request.body)
        
        # Extract data from callback
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        # Find payment by checkout request ID
        payment = Payment.objects.filter(
            response_data__CheckoutRequestID=checkout_request_id
        ).first()
        
        if not payment:
            return JsonResponse({
                'ResultCode': 1,
                'ResultDesc': 'Payment not found'
            })
        
        # Update payment based on result
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            # Extract transaction details
            mpesa_receipt = None
            amount = None
            phone = None
            transaction_date = None
            
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'MpesaReceiptNumber':
                    mpesa_receipt = value
                elif name == 'Amount':
                    amount = value
                elif name == 'PhoneNumber':
                    phone = value
                elif name == 'TransactionDate':
                    transaction_date = value
            
            # Update payment
            payment.status = 'completed'
            payment.mpesa_receipt = mpesa_receipt
            payment.completed_at = timezone.now()
            payment.response_data = callback_data
            payment.save()
            
            # Update order
            order = payment.order
            order.status = 'confirmed'
            order.confirmed_at = timezone.now()
            order.save()
            
        else:
            # Payment failed
            payment.status = 'failed'
            payment.failure_reason = result_desc
            payment.response_data = callback_data
            payment.save()
        
        return JsonResponse({
            'ResultCode': 0,
            'ResultDesc': 'Success'
        })
        
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': str(e)
        })


@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items'),
        id=order_id,
        user=request.user
    )
    
    payment = order.payments.filter(status='completed').first()
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payment_success.html', context)


@login_required
def payment_failed(request, order_id):
    """Payment failed page"""
    order = get_object_or_404(
        Order.objects.select_related('user'),
        id=order_id,
        user=request.user
    )
    
    payment = order.payments.first()
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payment_failed.html', context)


@login_required
def place_order(request):
    """Place order and create payment (Fixed version)"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get cart
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.items.select_related('product', 'variant').all()
                
                if not cart_items.exists():
                    messages.error(request, 'Your cart is empty')
                    return redirect('cart')
                
                # Get delivery details
                delivery_method = request.session.get('delivery_method', 'pickup_station')
                
                delivery_address = None
                pickup_station = None
                delivery_fee = Decimal('0.00')
                
                if delivery_method == 'home_delivery':
                    address_id = request.session.get('delivery_address_id')
                    if not address_id:
                        # Try to get from POST data
                        address_id = request.POST.get('delivery_address_id')
                    
                    if address_id:
                        delivery_address = get_object_or_404(Address, id=address_id, user=request.user)
                        
                        # Calculate delivery fee based on address location
                        delivery_zone = DeliveryZone.objects.filter(
                            region=delivery_address.region,
                            city=delivery_address.city,
                            is_active=True
                        ).first()
                        
                        if delivery_zone:
                            delivery_fee = delivery_zone.delivery_fee
                        else:
                            # Default fee if zone not found
                            delivery_fee = Decimal('300.00')
                            messages.warning(
                                request, 
                                f'Delivery zone for {delivery_address.city}, {delivery_address.region} not found. Using default fee of KSh 300.'
                            )
                    else:
                        messages.error(request, 'Please select a delivery address')
                        return redirect('checkout')
                        
                else:  # pickup_station
                    station_id = request.session.get('pickup_station_id')
                    if not station_id:
                        # Try to get from POST data
                        station_id = request.POST.get('pickup_station_id')
                    
                    if station_id:
                        pickup_station = get_object_or_404(PickupStation, id=station_id, is_active=True)
                        # Use pickup station's delivery fee
                        delivery_fee = pickup_station.delivery_fee
                    else:
                        # Use first available station as default
                        pickup_station = PickupStation.objects.filter(is_active=True).first()
                        if pickup_station:
                            delivery_fee = pickup_station.delivery_fee
                        else:
                            messages.error(request, 'No pickup stations available')
                            return redirect('checkout')
                
                # Calculate amounts
                subtotal = cart.subtotal
                
                # Apply discount
                discount = Decimal('0.00')
                coupon_code = request.session.get('coupon_code', '')
                
                if coupon_code:
                    try:
                        coupon = Coupon.objects.get(
                            code=coupon_code,
                            is_active=True,
                            valid_from__lte=timezone.now(),
                            valid_to__gte=timezone.now()
                        )
                        
                        # Validate minimum purchase
                        if subtotal >= coupon.minimum_purchase:
                            if coupon.discount_type == 'percentage':
                                discount = (subtotal * coupon.discount_value) / 100
                                if coupon.maximum_discount:
                                    discount = min(discount, coupon.maximum_discount)
                            else:
                                discount = coupon.discount_value
                            
                            # Increment usage count
                            coupon.usage_count += 1
                            coupon.save()
                        else:
                            # Remove invalid coupon
                            del request.session['coupon_code']
                            messages.warning(
                                request, 
                                f'Coupon requires minimum purchase of KSh {coupon.minimum_purchase}'
                            )
                    except Coupon.DoesNotExist:
                        # Remove invalid coupon
                        if 'coupon_code' in request.session:
                            del request.session['coupon_code']
                
                total = subtotal + delivery_fee - discount
                
                # Validate total
                if total <= 0:
                    messages.error(request, 'Invalid order total')
                    return redirect('checkout')
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    status='pending',
                    delivery_method=delivery_method,
                    delivery_address=delivery_address,
                    pickup_station=pickup_station,
                    subtotal=subtotal,
                    delivery_fee=delivery_fee,
                    discount=discount,
                    total=total,
                    customer_note=f'Coupon: {coupon_code}' if coupon_code else ''
                )
                
                # Create order items and update stock
                for cart_item in cart_items:
                    # Check stock availability
                    available_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock
                    
                    if available_stock < cart_item.quantity:
                        raise Exception(
                            f'Insufficient stock for {cart_item.product.name}. '
                            f'Only {available_stock} available.'
                        )
                    
                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        vendor=cart_item.product.vendor,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku,
                        variant_name=cart_item.variant.name if cart_item.variant else '',
                        quantity=cart_item.quantity,
                        price=cart_item.price,
                        total=cart_item.total_price
                    )
                    
                    # Update stock
                    if cart_item.variant:
                        cart_item.variant.stock -= cart_item.quantity
                        cart_item.variant.save()
                    
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.total_sales += cart_item.quantity
                    cart_item.product.save()
                
                # Get payment method
                payment_method = request.POST.get('payment_method', 'mpesa')
                
                # Validate payment method
                valid_payment_methods = ['mpesa', 'card', 'cash']
                if payment_method not in valid_payment_methods:
                    payment_method = 'mpesa'
                
                # Create payment
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=total,
                    status='pending'
                )
                
                # Clear cart
                cart.items.all().delete()
                
                # Clear session data
                session_keys_to_clear = [
                    'coupon_code',
                    'delivery_method',
                    'pickup_station_id',
                    'delivery_address_id'
                ]
                
                for key in session_keys_to_clear:
                    if key in request.session:
                        del request.session[key]
                
                # Save session
                request.session.modified = True
                
                messages.success(
                    request, 
                    f'Order {order.order_number} placed successfully! Total: KSh {total}'
                )
                
                # Redirect to payment page
                return redirect('payment_page', order_id=order.id)
                
        except Cart.DoesNotExist:
            messages.error(request, 'Your cart is empty')
            return redirect('cart')
        except Exception as e:
            messages.error(request, f'Error placing order: {str(e)}')
            return redirect('checkout')
    
    # If not POST, redirect to checkout
    return redirect('checkout')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, Payment, Review
from decimal import Decimal


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    
    # Get order with related data
    order = get_object_or_404(
        Order.objects.select_related(
            'user',
            'delivery_address',
            'pickup_station'
        ).prefetch_related(
            'items__product__images',
            'items__product__brand',
            'items__vendor',
            'payments'
        ),
        id=order_id,
        user=request.user
    )
    
    # Get order items grouped by vendor
    items_by_vendor = {}
    for item in order.items.all():
        vendor_id = item.vendor_id
        if vendor_id not in items_by_vendor:
            items_by_vendor[vendor_id] = {
                'vendor': item.vendor,
                'items': []
            }
        items_by_vendor[vendor_id]['items'].append(item)
    
    # Get payment information
    payment = order.payments.first()
    
    # Order status timeline
    status_timeline = [
        {
            'status': 'pending',
            'label': 'Order Placed',
            'date': order.created_at,
            'completed': True
        },
        {
            'status': 'confirmed',
            'label': 'Order Confirmed',
            'date': order.confirmed_at,
            'completed': order.confirmed_at is not None
        },
        {
            'status': 'processing',
            'label': 'Processing',
            'date': None,
            'completed': order.status in ['processing', 'shipped', 'delivered']
        },
        {
            'status': 'shipped',
            'label': 'Shipped',
            'date': order.shipped_at,
            'completed': order.shipped_at is not None
        },
        {
            'status': 'delivered',
            'label': 'Delivered',
            'date': order.delivered_at,
            'completed': order.delivered_at is not None
        }
    ]
    
    # Check if order is cancelled or returned
    if order.status in ['cancelled', 'returned', 'refunded']:
        status_timeline = [
            {
                'status': order.status,
                'label': order.get_status_display(),
                'date': order.updated_at,
                'completed': True
            }
        ]
    
    # Estimated delivery date
    estimated_delivery = None
    if order.delivery_method == 'pickup_station' and order.pickup_station:
        # Add 3-5 days for pickup
        from datetime import timedelta
        estimated_delivery = order.created_at + timedelta(days=5)
    elif order.delivery_address:
        # Check delivery zone for estimated days
        from .models import DeliveryZone
        delivery_zone = DeliveryZone.objects.filter(
            region=order.delivery_address.region,
            city=order.delivery_address.city,
            is_active=True
        ).first()
        if delivery_zone:
            from datetime import timedelta
            estimated_delivery = order.created_at + timedelta(days=delivery_zone.estimated_days)
    
    # Check which products can be reviewed
    reviewable_items = []
    if order.status == 'delivered':
        for item in order.items.all():
            # Check if user has already reviewed this product
            has_reviewed = Review.objects.filter(
                product=item.product,
                user=request.user
            ).exists()
            
            if not has_reviewed:
                reviewable_items.append(item.product.id)
    
    context = {
        'order': order,
        'items_by_vendor': items_by_vendor.values(),
        'payment': payment,
        'status_timeline': status_timeline,
        'estimated_delivery': estimated_delivery,
        'reviewable_items': reviewable_items,
    }
    
    return render(request, 'order_detail.html', context)


@login_required
def order_list(request):
    """User's order list"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        'delivery_address',
        'pickup_station'
    ).prefetch_related(
        'items__product__images'
    ).order_by('-created_at')
    
    # Apply status filter
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Get order counts by status
    from django.db.models import Count, Q
    status_counts = {
        'all': Order.objects.filter(user=request.user).count(),
        'pending': Order.objects.filter(user=request.user, status='pending').count(),
        'confirmed': Order.objects.filter(user=request.user, status='confirmed').count(),
        'shipped': Order.objects.filter(user=request.user, status='shipped').count(),
        'delivered': Order.objects.filter(user=request.user, status='delivered').count(),
        'cancelled': Order.objects.filter(user=request.user, status='cancelled').count(),
    }
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_counts': status_counts,
    }
    
    return render(request, 'order_list.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    if request.method == 'POST':
        try:
            order = get_object_or_404(
                Order.objects.select_related('user').prefetch_related('items__product'),
                id=order_id,
                user=request.user
            )
            
            # Check if order can be cancelled
            if order.status not in ['pending', 'confirmed']:
                messages.error(request, 'This order cannot be cancelled')
                return redirect('order_detail', order_id=order.id)
            
            # Cancel order
            order.status = 'cancelled'
            order.save()
            
            # Restore stock
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.total_sales -= item.quantity
                item.product.save()
            
            # Update payment status
            payment = order.payments.first()
            if payment and payment.status == 'completed':
                payment.status = 'refunded'
                payment.save()
            
            messages.success(request, f'Order {order.order_number} has been cancelled')
            return redirect('order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('order_detail', order_id=order_id)
    
    return redirect('order_list')


@login_required
def download_invoice(request, order_id):
    """Download order invoice as PDF"""
    order = get_object_or_404(
        Order.objects.select_related('user', 'delivery_address').prefetch_related('items'),
        id=order_id,
        user=request.user
    )
    
    # You can implement PDF generation here using libraries like:
    # - reportlab
    # - weasyprint
    # - xhtml2pdf
    
    # For now, return a simple response
    messages.info(request, 'Invoice download feature coming soon')
    return redirect('order_detail', order_id=order.id)


@login_required
def track_order(request, order_id):
    """Track order status"""
    order = get_object_or_404(
        Order.objects.select_related('user'),
        id=order_id,
        user=request.user
    )
    
    # Return tracking information as JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'tracking_number': order.tracking_number,
            'created_at': order.created_at.isoformat(),
            'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
            'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        })
    
    return redirect('order_detail', order_id=order.id)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q
from .models import User, Address, Order, Review, Wishlist, Notification
import json


@login_required
def account_overview(request):
    """Main account overview page"""
    user = request.user
    
    # Get statistics
    orders_count = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get default address
    default_address = Address.objects.filter(user=user, is_default=True).first()
    
    context = {
        'orders_count': orders_count,
        'pending_orders': pending_orders,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
        'default_address': default_address,
    }
    
    return render(request, 'account/overview.html', context)


@login_required
def account_orders(request):
    """User orders page"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'account/orders.html', context)


@login_required
def account_inbox(request):
    """User notifications/inbox"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'account/inbox.html', context)


@login_required
def account_reviews(request):
    """Pending reviews page"""
    # Get orders that can be reviewed (delivered orders)
    delivered_orders = Order.objects.filter(
        user=request.user,
        status='delivered'
    ).prefetch_related('items__product')
    
    # Get already reviewed products
    reviewed_products = Review.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    context = {
        'delivered_orders': delivered_orders,
        'reviewed_products': list(reviewed_products),
    }
    
    return render(request, 'account/reviews.html', context)


@login_required
def account_wishlist(request):
    """User wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'account/wishlist.html', context)


@login_required
def account_followed_sellers(request):
    """Followed sellers page - placeholder for future implementation"""
    context = {}
    return render(request, 'account/followed_sellers.html', context)


@login_required
def account_recently_viewed(request):
    """Recently viewed products - can be implemented with sessions"""
    context = {}
    return render(request, 'account/recently_viewed.html', context)


@login_required
def account_settings(request):
    """Account settings page"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone_number = request.POST.get('phone_number', '')
        user.date_of_birth = request.POST.get('date_of_birth', None)
        user.save()
        
        messages.success(request, 'Account details updated successfully')
        return redirect('account_settings')
    
    return render(request, 'account/settings.html')


@login_required
def account_address_book(request):
    """Address book page"""
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'addresses': addresses,
    }
    
    return render(request, 'account/address_book.html', context)


@login_required
def account_newsletter(request):
    """Newsletter preferences"""
    return render(request, 'account/newsletter.html')


# AJAX API Endpoints

@login_required
@require_http_methods(["POST"])
def api_add_address(request):
    """Add new address via AJAX"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['full_name', 'phone_number', 'region', 'city', 'area', 'street_address']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # If this is set as default, unset other defaults
        if data.get('is_default', False):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Create address
        address = Address.objects.create(
            user=request.user,
            address_type=data.get('address_type', 'home'),
            full_name=data['full_name'],
            phone_number=data['phone_number'],
            region=data['region'],
            city=data['city'],
            area=data['area'],
            street_address=data['street_address'],
            additional_info=data.get('additional_info', ''),
            is_default=data.get('is_default', False)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Address added successfully',
            'address': {
                'id': address.id,
                'full_name': address.full_name,
                'phone_number': address.phone_number,
                'address_type': address.address_type,
                'region': address.region,
                'city': address.city,
                'area': address.area,
                'street_address': address.street_address,
                'additional_info': address.additional_info,
                'is_default': address.is_default,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_get_address(request, address_id):
    """Get address details via AJAX"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'address': {
                'id': address.id,
                'full_name': address.full_name,
                'phone_number': address.phone_number,
                'address_type': address.address_type,
                'region': address.region,
                'city': address.city,
                'area': address.area,
                'street_address': address.street_address,
                'additional_info': address.additional_info,
                'is_default': address.is_default,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)


@login_required
@require_http_methods(["PUT", "POST"])
def api_update_address(request, address_id):
    """Update address via AJAX"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        data = json.loads(request.body)
        
        # Update fields
        address.full_name = data.get('full_name', address.full_name)
        address.phone_number = data.get('phone_number', address.phone_number)
        address.address_type = data.get('address_type', address.address_type)
        address.region = data.get('region', address.region)
        address.city = data.get('city', address.city)
        address.area = data.get('area', address.area)
        address.street_address = data.get('street_address', address.street_address)
        address.additional_info = data.get('additional_info', address.additional_info)
        
        # Handle default address
        if data.get('is_default', False):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
        
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Address updated successfully',
            'address': {
                'id': address.id,
                'full_name': address.full_name,
                'phone_number': address.phone_number,
                'address_type': address.address_type,
                'region': address.region,
                'city': address.city,
                'area': address.area,
                'street_address': address.street_address,
                'additional_info': address.additional_info,
                'is_default': address.is_default,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE", "POST"])
def api_delete_address(request, address_id):
    """Delete address via AJAX"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Don't allow deleting default address if it's the only one
        if address.is_default and Address.objects.filter(user=request.user).count() > 1:
            # Set another address as default
            next_address = Address.objects.filter(user=request.user).exclude(id=address_id).first()
            if next_address:
                next_address.is_default = True
                next_address.save()
        
        address.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Address deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_set_default_address(request, address_id):
    """Set address as default via AJAX"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Unset all other defaults
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this as default
        address.is_default = True
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Default address updated'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """Mark all notifications as read"""
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)