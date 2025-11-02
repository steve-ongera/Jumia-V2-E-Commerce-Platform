from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, Address, PickupStation, Category, Brand, Vendor, 
    Product, ProductImage, ProductVariant, ProductSpecification,
    Review, Cart, CartItem, Order, OrderItem, Payment, 
    Coupon, Wishlist, Notification, DeliveryZone, Banner
)


# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_vendor', 'is_verified', 'date_joined']
    list_filter = ['is_vendor', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'email', 'phone_number', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_verified', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'region', 'address_type', 'is_default', 'created_at']
    list_filter = ['address_type', 'region', 'city', 'is_default']
    search_fields = ['full_name', 'phone_number', 'city', 'region', 'user__username']
    date_hierarchy = 'created_at'


# Pickup Station Admin
@admin.register(PickupStation)
class PickupStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'region', 'phone_number', 'is_active', 'capacity']
    list_filter = ['region', 'city', 'is_active']
    search_fields = ['name', 'code', 'city', 'region']
    list_editable = ['is_active']


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


# Vendor Admin
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'phone', 'is_verified', 'is_active', 'rating', 'commission_rate', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['business_name', 'business_registration', 'user__username', 'email']
    prepopulated_fields = {'slug': ('business_name',)}
    readonly_fields = ['created_at', 'rating']
    list_editable = ['is_verified', 'is_active', 'commission_rate']


# Product Inline Admin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'price', 'stock', 'is_active']


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ['name', 'value', 'order']


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'vendor', 'category', 'brand', 
        'price_display', 'stock_status', 'is_featured', 
        'is_active', 'views', 'total_sales', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'brand', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views', 'total_sales', 'created_at', 'updated_at', 'average_rating']
    list_editable = ['is_active', 'is_featured']
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'category', 'brand', 'name', 'slug', 'sku')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold', 'weight')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'total_sales', 'average_rating', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        if obj.compare_price and obj.compare_price > obj.price:
            return format_html(
                '<span style="color: red;">KES {}</span> <s>KES {}</s> <span style="color: green;">-{}%</span>',
                obj.price, obj.compare_price, obj.discount_percentage
            )
        return f'KES {obj.price}'
    price_display.short_description = 'Price'
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.stock <= obj.low_stock_threshold:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock)
        return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock)
    stock_status.short_description = 'Stock Status'


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'helpful_count']
    list_editable = ['is_approved']
    date_hierarchy = 'created_at'


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'cart_total', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    
    def cart_total(self, obj):
        return f'KES {obj.subtotal}'
    cart_total.short_description = 'Total'


# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'product_name', 'quantity', 'price', 'total']
    can_delete = False


# Payment Inline
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['transaction_id', 'payment_method', 'status', 'amount', 'created_at']
    can_delete = False


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'delivery_method',
        'total_display', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'delivery_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'tracking_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, PaymentInline]
    list_editable = ['status']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'tracking_number')
        }),
        ('Delivery', {
            'fields': ('delivery_method', 'delivery_address', 'pickup_station')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'tax', 'discount', 'total')
        }),
        ('Notes', {
            'fields': ('customer_note', 'admin_note')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return f'KES {obj.total}'
    total_display.short_description = 'Total'
    
    def payment_status(self, obj):
        payment = obj.payments.first()
        if payment:
            colors = {
                'completed': 'green',
                'pending': 'orange',
                'failed': 'red',
                'processing': 'blue',
            }
            color = colors.get(payment.status, 'gray')
            return format_html(
                '<span style="color: {};">{}</span>',
                color, payment.get_status_display()
            )
        return format_html('<span style="color: red;">No Payment</span>')
    payment_status.short_description = 'Payment'


# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'order', 'payment_method', 'status',
        'amount_display', 'created_at', 'completed_at'
    ]
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'mpesa_receipt', 'mpesa_phone']
    readonly_fields = ['transaction_id', 'created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'transaction_id', 'payment_method', 'status', 'amount')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_receipt', 'mpesa_phone'),
            'classes': ('collapse',)
        }),
        ('Card Details', {
            'fields': ('card_last4', 'card_brand'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('response_data', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def amount_display(self, obj):
        colors = {
            'completed': 'green',
            'failed': 'red',
            'pending': 'orange',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">KES {}</span>',
            color, obj.amount
        )
    amount_display.short_description = 'Amount'


# Coupon Admin
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_display', 'minimum_purchase',
        'usage_display', 'valid_from', 'valid_to', 'is_active'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['usage_count', 'created_at']
    list_editable = ['is_active']
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f'{obj.discount_value}%'
        return f'KES {obj.discount_value}'
    discount_display.short_description = 'Discount'
    
    def usage_display(self, obj):
        if obj.usage_limit:
            return f'{obj.usage_count}/{obj.usage_limit}'
        return f'{obj.usage_count}/∞'
    usage_display.short_description = 'Usage'


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    date_hierarchy = 'created_at'


# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'


# Delivery Zone Admin
@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['region', 'city', 'delivery_fee', 'estimated_days', 'is_active']
    list_filter = ['region', 'is_active']
    search_fields = ['region', 'city']
    list_editable = ['delivery_fee', 'estimated_days', 'is_active']


# Banner Admin
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_preview', 'order', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'subtitle']
    list_editable = ['order', 'is_active']
    
    def banner_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="50" />')
        return "No Image"
    banner_preview.short_description = 'Preview'


# Admin Site Customization
admin.site.site_header = "Jumia V2 Admin"
admin.site.site_title = "Jumia V2"
admin.site.index_title = "Welcome to Jumia V2 Administration"