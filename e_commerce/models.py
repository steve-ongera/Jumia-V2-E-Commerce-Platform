from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
import uuid


class User(AbstractUser):
    """Extended user model"""
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    is_vendor = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'


class Address(models.Model):
    """User addresses for delivery"""
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    street_address = models.TextField()
    additional_info = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.region}"


class PickupStation(models.Model):
    """Jumia pickup stations"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    operating_hours = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    capacity = models.IntegerField(default=100)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    
    class Meta:
        db_table = 'pickup_stations'
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Category(models.Model):
    """Product categories with hierarchy"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """Product brands"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'brands'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Vendor(models.Model):
    """Vendor/Seller information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='vendors/', null=True, blank=True)
    business_registration = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vendors'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.business_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.business_name


class Product(models.Model):
    """Main product model"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Weight in KG")
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    views = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """Product variants (size, color, etc.)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="e.g., Size: Large, Color: Red")
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductSpecification(models.Model):
    """Product specifications/attributes"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_specifications'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    """Product reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Cart(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):
    """Cart items"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'cart_items'
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Order(models.Model):
    """Orders"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    )
    
    DELIVERY_METHOD = (
        ('home_delivery', 'Home Delivery'),
        ('pickup_station', 'Pickup Station'),
    )
    
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Delivery information
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD)
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_station = models.ForeignKey(PickupStation, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Order notes
    customer_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """Order items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    
    product_name = models.CharField(max_length=300)
    product_sku = models.CharField(max_length=100)
    variant_name = models.CharField(max_length=100, blank=True)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_items'
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class Payment(models.Model):
    """Payment transactions"""
    PAYMENT_METHOD = (
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Delivery'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # M-Pesa specific fields
    mpesa_receipt = models.CharField(max_length=100, blank=True)
    mpesa_phone = models.CharField(max_length=15, blank=True)
    
    # Card specific fields
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    
    # Additional info
    response_data = models.JSONField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.payment_method}"


class Coupon(models.Model):
    """Discount coupons"""
    DISCOUNT_TYPE = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    user_limit = models.IntegerField(default=1)
    
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupons'
    
    def __str__(self):
        return self.code


class Wishlist(models.Model):
    """User wishlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlists'
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPE = (
        ('order', 'Order Update'),
        ('payment', 'Payment'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class DeliveryZone(models.Model):
    """Delivery zones and pricing"""
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(help_text="Estimated delivery days")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'delivery_zones'
        unique_together = ['region', 'city']
    
    def __str__(self):
        return f"{self.city}, {self.region}"


class Banner(models.Model):
    """Homepage banners/sliders"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=200, blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'banners'
        ordering = ['order']
    
    def __str__(self):
        return self.title