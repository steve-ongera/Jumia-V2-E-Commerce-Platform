"""
Django management command to seed database with real Kenyan e-commerce data
File location: e_commerce/management/commands/seed_data.py

Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from e_commerce.models import (
    User, Address, PickupStation, Category, Brand, Vendor,
    Product, ProductImage, ProductVariant, ProductSpecification,
    Review, Order, OrderItem, Payment, Coupon, DeliveryZone, Banner
)


class Command(BaseCommand):
    help = 'Seeds the database with real Kenyan e-commerce data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data seeding...')
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('Clearing existing data...')
        # self.clear_data()
        
        # Seed data in order
        self.seed_users()
        self.seed_delivery_zones()
        self.seed_pickup_stations()
        self.seed_categories()
        self.seed_brands()
        self.seed_vendors()
        self.seed_products()
        self.seed_coupons()
        self.seed_banners()
        self.seed_orders()
        
        self.stdout.write(self.style.SUCCESS('✅ Data seeding completed successfully!'))

    def clear_data(self):
        """Clear all data from models"""
        models = [Order, OrderItem, Payment, Review, Product, 
                  ProductImage, ProductVariant, ProductSpecification,
                  Vendor, Brand, Category, PickupStation, 
                  DeliveryZone, Address, Coupon, Banner]
        for model in models:
            model.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def seed_users(self):
        """Create users"""
        self.stdout.write('Seeding users...')
        
        users_data = [
            {
                'username': 'john_kamau',
                'email': 'john.kamau@gmail.com',
                'first_name': 'John',
                'last_name': 'Kamau',
                'phone_number': '0712345678',
                'is_vendor': False
            },
            {
                'username': 'mary_wanjiku',
                'email': 'mary.wanjiku@gmail.com',
                'first_name': 'Mary',
                'last_name': 'Wanjiku',
                'phone_number': '0723456789',
                'is_vendor': False
            },
            {
                'username': 'peter_omondi',
                'email': 'peter.omondi@gmail.com',
                'first_name': 'Peter',
                'last_name': 'Omondi',
                'phone_number': '0734567890',
                'is_vendor': True
            },
            {
                'username': 'grace_akinyi',
                'email': 'grace.akinyi@gmail.com',
                'first_name': 'Grace',
                'last_name': 'Akinyi',
                'phone_number': '0745678901',
                'is_vendor': False
            },
            {
                'username': 'james_mwangi',
                'email': 'james.mwangi@gmail.com',
                'first_name': 'James',
                'last_name': 'Mwangi',
                'phone_number': '0756789012',
                'is_vendor': True
            },
            {
                'username': 'anne_njeri',
                'email': 'anne.njeri@gmail.com',
                'first_name': 'Anne',
                'last_name': 'Njeri',
                'phone_number': '0767890123',
                'is_vendor': False
            },
            {
                'username': 'david_kipchoge',
                'email': 'david.kipchoge@gmail.com',
                'first_name': 'David',
                'last_name': 'Kipchoge',
                'phone_number': '0778901234',
                'is_vendor': True
            },
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    **user_data,
                    'password': make_password('password123'),
                    'is_verified': True,
                }
            )
            created_users.append(user)
            if created:
                # Create addresses for non-vendor users
                if not user.is_vendor:
                    self.create_addresses(user)
        
        self.users = created_users
        self.stdout.write(f'✓ Created {len(created_users)} users')

    def create_addresses(self, user):
        """Create addresses for a user"""
        addresses_data = [
            {
                'address_type': 'home',
                'full_name': f'{user.first_name} {user.last_name}',
                'phone_number': user.phone_number,
                'region': 'Nairobi',
                'city': 'Nairobi',
                'area': 'Westlands',
                'street_address': 'Muthithi Road, House No. 45',
                'is_default': True
            },
            {
                'address_type': 'work',
                'full_name': f'{user.first_name} {user.last_name}',
                'phone_number': user.phone_number,
                'region': 'Nairobi',
                'city': 'Nairobi',
                'area': 'Upperhill',
                'street_address': 'Ngong Road, ABC Place 3rd Floor',
                'is_default': False
            }
        ]
        
        for addr_data in addresses_data:
            Address.objects.get_or_create(
                user=user,
                address_type=addr_data['address_type'],
                defaults=addr_data
            )

    def seed_delivery_zones(self):
        """Create delivery zones across Kenya"""
        self.stdout.write('Seeding delivery zones...')
        
        zones_data = [
            # Nairobi
            {'region': 'Nairobi', 'city': 'Nairobi CBD', 'delivery_fee': 200, 'estimated_days': 1},
            {'region': 'Nairobi', 'city': 'Westlands', 'delivery_fee': 250, 'estimated_days': 1},
            {'region': 'Nairobi', 'city': 'Eastlands', 'delivery_fee': 250, 'estimated_days': 1},
            {'region': 'Nairobi', 'city': 'Karen', 'delivery_fee': 300, 'estimated_days': 1},
            {'region': 'Nairobi', 'city': 'Kileleshwa', 'delivery_fee': 250, 'estimated_days': 1},
            
            # Mombasa
            {'region': 'Mombasa', 'city': 'Mombasa CBD', 'delivery_fee': 300, 'estimated_days': 2},
            {'region': 'Mombasa', 'city': 'Nyali', 'delivery_fee': 350, 'estimated_days': 2},
            {'region': 'Mombasa', 'city': 'Bamburi', 'delivery_fee': 400, 'estimated_days': 2},
            
            # Kisumu
            {'region': 'Kisumu', 'city': 'Kisumu Town', 'delivery_fee': 400, 'estimated_days': 3},
            {'region': 'Kisumu', 'city': 'Milimani', 'delivery_fee': 450, 'estimated_days': 3},
            
            # Nakuru
            {'region': 'Nakuru', 'city': 'Nakuru Town', 'delivery_fee': 350, 'estimated_days': 2},
            {'region': 'Nakuru', 'city': 'Milimani', 'delivery_fee': 400, 'estimated_days': 2},
            
            # Eldoret
            {'region': 'Uasin Gishu', 'city': 'Eldoret', 'delivery_fee': 450, 'estimated_days': 3},
            
            # Thika
            {'region': 'Kiambu', 'city': 'Thika', 'delivery_fee': 300, 'estimated_days': 2},
            {'region': 'Kiambu', 'city': 'Ruiru', 'delivery_fee': 250, 'estimated_days': 1},
            {'region': 'Kiambu', 'city': 'Kikuyu', 'delivery_fee': 300, 'estimated_days': 2},
            
            # Machakos
            {'region': 'Machakos', 'city': 'Machakos Town', 'delivery_fee': 350, 'estimated_days': 2},
            {'region': 'Machakos', 'city': 'Athi River', 'delivery_fee': 300, 'estimated_days': 2},
        ]
        
        for zone_data in zones_data:
            DeliveryZone.objects.get_or_create(
                region=zone_data['region'],
                city=zone_data['city'],
                defaults=zone_data
            )
        
        self.stdout.write(f'✓ Created {len(zones_data)} delivery zones')

    def seed_pickup_stations(self):
        """Create pickup stations"""
        self.stdout.write('Seeding pickup stations...')
        
        stations_data = [
            {
                'name': 'Jumia Pickup Station - Sarit Centre',
                'code': 'NRB-SAR-001',
                'region': 'Nairobi',
                'city': 'Westlands',
                'address': 'Sarit Centre, Ground Floor, Westlands, Nairobi',
                'phone_number': '0709170000',
                'operating_hours': 'Mon-Sat: 9AM-8PM, Sun: 10AM-6PM',
                'capacity': 150
            },
            {
                'name': 'Jumia Pickup Station - The Hub',
                'code': 'NRB-HUB-002',
                'region': 'Nairobi',
                'city': 'Karen',
                'address': 'The Hub Karen, Karen Road, Nairobi',
                'phone_number': '0709170001',
                'operating_hours': 'Mon-Sat: 9AM-8PM, Sun: 10AM-6PM',
                'capacity': 100
            },
            {
                'name': 'Jumia Pickup Station - Garden City',
                'code': 'NRB-GC-003',
                'region': 'Nairobi',
                'city': 'Thika Road',
                'address': 'Garden City Mall, Thika Road, Nairobi',
                'phone_number': '0709170002',
                'operating_hours': 'Mon-Sun: 10AM-9PM',
                'capacity': 200
            },
            {
                'name': 'Jumia Pickup Station - Two Rivers',
                'code': 'NRB-TR-004',
                'region': 'Nairobi',
                'city': 'Ruaka',
                'address': 'Two Rivers Mall, Limuru Road, Nairobi',
                'phone_number': '0709170003',
                'operating_hours': 'Mon-Sun: 10AM-9PM',
                'capacity': 180
            },
            {
                'name': 'Jumia Pickup Station - Mombasa City Mall',
                'code': 'MSA-CM-001',
                'region': 'Mombasa',
                'city': 'Mombasa',
                'address': 'City Mall, Nyerere Avenue, Mombasa',
                'phone_number': '0709180000',
                'operating_hours': 'Mon-Sat: 9AM-8PM, Sun: 10AM-6PM',
                'capacity': 120
            },
            {
                'name': 'Jumia Pickup Station - Nakumatt Nakuru',
                'code': 'NKR-NK-001',
                'region': 'Nakuru',
                'city': 'Nakuru',
                'address': 'Kenyatta Avenue, Nakuru Town',
                'phone_number': '0709190000',
                'operating_hours': 'Mon-Sat: 9AM-7PM',
                'capacity': 80
            },
            {
                'name': 'Jumia Pickup Station - Kisumu',
                'code': 'KSM-KS-001',
                'region': 'Kisumu',
                'city': 'Kisumu',
                'address': 'Oginga Odinga Street, Kisumu',
                'phone_number': '0709200000',
                'operating_hours': 'Mon-Sat: 9AM-7PM',
                'capacity': 70
            },
            {
                'name': 'Jumia Pickup Station - Eldoret',
                'code': 'ELD-EL-001',
                'region': 'Uasin Gishu',
                'city': 'Eldoret',
                'address': 'Uganda Road, Eldoret Town',
                'phone_number': '0709210000',
                'operating_hours': 'Mon-Sat: 9AM-7PM',
                'capacity': 90
            },
            {
                'name': 'Jumia Pickup Station - Thika',
                'code': 'THK-TH-001',
                'region': 'Kiambu',
                'city': 'Thika',
                'address': 'Commercial Street, Thika Town',
                'phone_number': '0709220000',
                'operating_hours': 'Mon-Sat: 9AM-7PM',
                'capacity': 60
            },
        ]
        
        for station_data in stations_data:
            PickupStation.objects.get_or_create(
                code=station_data['code'],
                defaults=station_data
            )
        
        self.stdout.write(f'✓ Created {len(stations_data)} pickup stations')

    def seed_categories(self):
        """Create product categories"""
        self.stdout.write('Seeding categories...')
        
        # Main categories
        electronics = Category.objects.get_or_create(
            name='Electronics', 
            defaults={'description': 'Electronic devices and gadgets'}
        )[0]
        
        fashion = Category.objects.get_or_create(
            name='Fashion',
            defaults={'description': 'Clothing, shoes, and accessories'}
        )[0]
        
        home = Category.objects.get_or_create(
            name='Home & Kitchen',
            defaults={'description': 'Home appliances and kitchen items'}
        )[0]
        
        phones = Category.objects.get_or_create(
            name='Phones & Tablets',
            defaults={'description': 'Mobile phones and tablets'}
        )[0]
        
        computers = Category.objects.get_or_create(
            name='Computing',
            defaults={'description': 'Laptops, desktops, and accessories'}
        )[0]
        
        health = Category.objects.get_or_create(
            name='Health & Beauty',
            defaults={'description': 'Health and beauty products'}
        )[0]
        
        sports = Category.objects.get_or_create(
            name='Sports & Outdoors',
            defaults={'description': 'Sports equipment and outdoor gear'}
        )[0]
        
        # Sub-categories for Electronics
        Category.objects.get_or_create(name='Televisions', parent=electronics)
        Category.objects.get_or_create(name='Audio & Sound', parent=electronics)
        Category.objects.get_or_create(name='Cameras', parent=electronics)
        
        # Sub-categories for Phones
        Category.objects.get_or_create(name='Smartphones', parent=phones)
        Category.objects.get_or_create(name='Tablets', parent=phones)
        Category.objects.get_or_create(name='Phone Accessories', parent=phones)
        
        # Sub-categories for Fashion
        Category.objects.get_or_create(name='Men\'s Fashion', parent=fashion)
        Category.objects.get_or_create(name='Women\'s Fashion', parent=fashion)
        Category.objects.get_or_create(name='Kids Fashion', parent=fashion)
        Category.objects.get_or_create(name='Shoes', parent=fashion)
        
        # Sub-categories for Home
        Category.objects.get_or_create(name='Kitchen Appliances', parent=home)
        Category.objects.get_or_create(name='Furniture', parent=home)
        Category.objects.get_or_create(name='Bedding', parent=home)
        
        # Sub-categories for Computing
        Category.objects.get_or_create(name='Laptops', parent=computers)
        Category.objects.get_or_create(name='Desktops', parent=computers)
        Category.objects.get_or_create(name='Computer Accessories', parent=computers)
        
        self.stdout.write('✓ Created categories with sub-categories')

    def seed_brands(self):
        """Create brands"""
        self.stdout.write('Seeding brands...')
        
        brands_data = [
            'Samsung', 'Apple', 'Xiaomi', 'Oppo', 'Tecno', 'Infinix',
            'Nokia', 'Huawei', 'Realme', 'Vivo', 'OnePlus',
            'HP', 'Dell', 'Lenovo', 'Asus', 'Acer',
            'Sony', 'LG', 'TCL', 'Hisense', 'Skyworth',
            'Adidas', 'Nike', 'Puma', 'Reebok',
            'Ramtons', 'Hotpoint', 'Von', 'Mika', 'Sayona'
        ]
        
        for brand_name in brands_data:
            Brand.objects.get_or_create(
                name=brand_name,
                defaults={'description': f'{brand_name} official products'}
            )
        
        self.stdout.write(f'✓ Created {len(brands_data)} brands')

    def seed_vendors(self):
        """Create vendors"""
        self.stdout.write('Seeding vendors...')
        
        vendor_users = User.objects.filter(is_vendor=True)
        
        vendors_data = [
            {
                'business_name': 'TechHub Kenya',
                'description': 'Leading supplier of electronics and gadgets in Kenya',
                'business_registration': 'BN/2020/12345',
                'tax_id': 'P051234567A',
                'phone': '0712000001',
                'email': 'info@techhubke.com',
                'address': 'Moi Avenue, Nairobi',
                'commission_rate': 12.00,
                'is_verified': True,
                'rating': 4.5
            },
            {
                'business_name': 'Fashion Express Kenya',
                'description': 'Quality fashion for men, women and children',
                'business_registration': 'BN/2019/54321',
                'tax_id': 'P051234568B',
                'phone': '0723000002',
                'email': 'sales@fashionexpress.co.ke',
                'address': 'Tom Mboya Street, Nairobi',
                'commission_rate': 15.00,
                'is_verified': True,
                'rating': 4.3
            },
            {
                'business_name': 'HomeStyle Appliances',
                'description': 'Home and kitchen appliances at affordable prices',
                'business_registration': 'BN/2021/98765',
                'tax_id': 'P051234569C',
                'phone': '0734000003',
                'email': 'contact@homestyleke.com',
                'address': 'Biashara Street, Nairobi',
                'commission_rate': 13.00,
                'is_verified': True,
                'rating': 4.7
            },
        ]
        
        self.vendors = []
        for i, vendor_data in enumerate(vendors_data):
            if i < len(vendor_users):
                vendor, created = Vendor.objects.get_or_create(
                    user=vendor_users[i],
                    defaults=vendor_data
                )
                self.vendors.append(vendor)
        
        self.stdout.write(f'✓ Created {len(self.vendors)} vendors')

    def seed_products(self):
        """Create products"""
        self.stdout.write('Seeding products...')
        
        products_data = [
            # Smartphones
            {
                'name': 'Samsung Galaxy A54 5G 256GB',
                'category': 'Smartphones',
                'brand': 'Samsung',
                'description': 'Experience blazing-fast 5G speeds with the Samsung Galaxy A54. Features a stunning 6.4" Super AMOLED display, 50MP triple camera system, and powerful Exynos 1380 processor. Perfect for multitasking, gaming, and capturing life\'s moments.',
                'short_description': '6.4" Super AMOLED, 50MP Camera, 5000mAh Battery',
                'price': 45999,
                'compare_price': 52999,
                'stock': 45,
                'specifications': {
                    'Display': '6.4" Super AMOLED',
                    'RAM': '8GB',
                    'Storage': '256GB',
                    'Camera': '50MP + 12MP + 5MP',
                    'Battery': '5000mAh',
                    'OS': 'Android 13'
                }
            },
            {
                'name': 'Tecno Spark 10 Pro 256GB',
                'category': 'Smartphones',
                'brand': 'Tecno',
                'description': 'The Tecno Spark 10 Pro delivers exceptional value with its 6.8" display, 32MP selfie camera, and massive 5000mAh battery. Includes 8GB RAM expandable to 16GB for smooth performance.',
                'short_description': '6.8" Display, 32MP Selfie, 5000mAh, 8GB RAM',
                'price': 18999,
                'compare_price': 23999,
                'stock': 120,
                'specifications': {
                    'Display': '6.8" IPS LCD',
                    'RAM': '8GB + 8GB Extended',
                    'Storage': '256GB',
                    'Camera': '50MP + AI Lens',
                    'Battery': '5000mAh',
                    'OS': 'Android 13'
                }
            },
            {
                'name': 'Infinix Note 30 VIP 256GB',
                'category': 'Smartphones',
                'brand': 'Infinix',
                'description': 'Premium features at an affordable price. The Infinix Note 30 VIP boasts 68W fast charging, 108MP camera, and AMOLED display. Get a full charge in just 30 minutes!',
                'short_description': '68W Fast Charging, 108MP Camera, AMOLED Display',
                'price': 32999,
                'compare_price': 37999,
                'stock': 67,
                'specifications': {
                    'Display': '6.67" AMOLED',
                    'RAM': '12GB',
                    'Storage': '256GB',
                    'Camera': '108MP + 2MP + 2MP',
                    'Battery': '5000mAh with 68W Charging',
                    'OS': 'Android 13'
                }
            },
            {
                'name': 'Xiaomi Redmi Note 12 Pro 5G',
                'category': 'Smartphones',
                'brand': 'Xiaomi',
                'description': '5G connectivity meets powerful performance. Features a 200MP camera, 120Hz AMOLED display, and Snapdragon 732G processor. Perfect for content creators.',
                'short_description': '200MP Camera, 5G, 120Hz AMOLED',
                'price': 38999,
                'compare_price': 44999,
                'stock': 55,
                'specifications': {
                    'Display': '6.67" AMOLED 120Hz',
                    'RAM': '8GB',
                    'Storage': '256GB',
                    'Camera': '200MP + 8MP + 2MP',
                    'Battery': '5000mAh',
                    'OS': 'MIUI 14'
                }
            },
            
            # Laptops
            {
                'name': 'HP Pavilion 15 - Intel Core i5 11th Gen, 8GB RAM, 512GB SSD',
                'category': 'Laptops',
                'brand': 'HP',
                'description': 'Powerful performance for work and play. The HP Pavilion 15 features 11th Gen Intel Core i5, 8GB RAM, and fast 512GB SSD storage. Perfect for students and professionals.',
                'short_description': 'Intel i5 11th Gen, 8GB RAM, 512GB SSD, 15.6" FHD',
                'price': 62999,
                'compare_price': 72999,
                'stock': 28,
                'specifications': {
                    'Processor': 'Intel Core i5-1135G7',
                    'RAM': '8GB DDR4',
                    'Storage': '512GB SSD',
                    'Display': '15.6" FHD',
                    'Graphics': 'Intel Iris Xe',
                    'OS': 'Windows 11'
                }
            },
            {
                'name': 'Lenovo IdeaPad 3 - AMD Ryzen 5, 16GB RAM, 512GB SSD',
                'category': 'Laptops',
                'brand': 'Lenovo',
                'description': 'Exceptional multitasking with 16GB RAM and AMD Ryzen 5 processor. Features a comfortable keyboard and long battery life. Great for productivity.',
                'short_description': 'AMD Ryzen 5, 16GB RAM, 512GB SSD, 15.6"',
                'price': 68999,
                'compare_price': 78999,
                'stock': 22,
                'specifications': {
                    'Processor': 'AMD Ryzen 5 5500U',
                    'RAM': '16GB DDR4',
                    'Storage': '512GB SSD',
                    'Display': '15.6" FHD',
                    'Graphics': 'AMD Radeon',
                    'OS': 'Windows 11'
                }
            },
            {
                'name': 'Dell Inspiron 15 3000 - Intel Core i3, 4GB RAM, 1TB HDD',
                'category': 'Laptops',
                'brand': 'Dell',
                'description': 'Affordable laptop for basic computing needs. Perfect for students and home use. Includes 1TB storage for all your files.',
                'short_description': 'Intel i3, 4GB RAM, 1TB HDD, Budget-Friendly',
                'price': 38999,
                'compare_price': 44999,
                'stock': 40,
                'specifications': {
                    'Processor': 'Intel Core i3-1115G4',
                    'RAM': '4GB DDR4',
                    'Storage': '1TB HDD',
                    'Display': '15.6" HD',
                    'Graphics': 'Intel UHD',
                    'OS': 'Windows 11'
                }
            },
            
            # Televisions
            {
                'name': 'Samsung 43 Inch Smart TV Full HD',
                'category': 'Televisions',
                'brand': 'Samsung',
                'description': 'Immersive entertainment experience with Samsung Smart TV. Access Netflix, YouTube, and more. Crystal clear Full HD display with vibrant colors.',
                'short_description': '43" Full HD, Smart TV, Built-in WiFi',
                'price': 32999,
                'compare_price': 38999,
                'stock': 35,
                'specifications': {
                    'Screen Size': '43 inches',
                    'Resolution': '1920 x 1080 Full HD',
                    'Smart TV': 'Yes - Tizen OS',
                    'Ports': '2 HDMI, 1 USB',
                    'Sound': '20W Speakers'
                }
            },
            {
                'name': 'TCL 55 Inch 4K UHD Android Smart TV',
                'category': 'Televisions',
                'brand': 'TCL',
                'description': 'Stunning 4K resolution with Android TV. Access Google Play Store for unlimited entertainment. HDR support for enhanced picture quality.',
                'short_description': '55" 4K UHD, Android TV, HDR',
                'price': 48999,
                'compare_price': 56999,
                'stock': 30,
                'specifications': {
                    'Screen Size': '55 inches',
                    'Resolution': '3840 x 2160 4K UHD',
                    'Smart TV': 'Yes - Android TV',
                    'HDR': 'Yes',
                    'Ports': '3 HDMI, 2 USB',
                    'Sound': '24W Dolby Audio'
                }
            },
            {
                'name': 'Hisense 32 Inch HD LED TV',
                'category': 'Televisions',
                'brand': 'Hisense',
                'description': 'Compact and affordable HD TV perfect for bedrooms and small spaces. Energy efficient with clear picture quality.',
                'short_description': '32" HD LED, Energy Efficient, USB Playback',
                'price': 15999,
                'compare_price': 19999,
                'stock': 60,
                'specifications': {
                    'Screen Size': '32 inches',
                    'Resolution': '1366 x 768 HD',
                    'Smart TV': 'No',
                    'Ports': '2 HDMI, 1 USB',
                    'Sound': '16W Speakers'
                }
            },
            
            # Kitchen Appliances
            {
                'name': 'Ramtons 4 Burner Gas Cooker with Oven',
                'category': 'Kitchen Appliances',
                'brand': 'Ramtons',
                'description': 'Professional cooking experience at home. Features 4 gas burners, spacious oven, and auto-ignition. Durable stainless steel construction.',
                'short_description': '4 Burner, Auto Ignition, Stainless Steel',
                'price': 25999,
                'compare_price': 31999,
                'stock': 25,
                'specifications': {
                    'Burners': '4 Gas Burners',
                    'Oven': 'Yes - 60L Capacity',
                    'Ignition': 'Auto Ignition',
                    'Material': 'Stainless Steel',
                    'Dimensions': '60cm x 60cm'
                }
            },
            {
                'name': 'Von Hotpoint 200L Double Door Refrigerator',
                'category': 'Kitchen Appliances',
                'brand': 'Von',
                'description': 'Keep your food fresh with this energy-efficient refrigerator. Features separate freezer compartment, adjustable shelves, and LED lighting.',
                'short_description': '200L Capacity, Energy Efficient, LED Light',
                'price': 34999,
                'compare_price': 41999,
                'stock': 18,
                'specifications': {
                    'Capacity': '200 Liters',
                    'Type': 'Double Door',
                    'Freezer': '50L',
                    'Energy Rating': 'A+',
                    'Color': 'Silver'
                }
            },
            {
                'name': 'Mika 1.8L Electric Kettle - Stainless Steel',
                'category': 'Kitchen Appliances',
                'brand': 'Mika',
                'description': 'Fast boiling electric kettle with 1.8L capacity. Auto shut-off and boil-dry protection for safety. Perfect for tea and coffee lovers.',
                'short_description': '1.8L, Auto Shut-off, Stainless Steel',
                'price': 1899,
                'compare_price': 2499,
                'stock': 100,
                'specifications': {
                    'Capacity': '1.8 Liters',
                    'Power': '2000W',
                    'Material': 'Stainless Steel',
                    'Features': 'Auto Shut-off, Boil-dry Protection',
                    'Warranty': '1 Year'
                }
            },
            {
                'name': 'Sayona 5L Rice Cooker with Steamer',
                'category': 'Kitchen Appliances',
                'brand': 'Sayona',
                'description': 'Cook perfect rice every time. Large 5L capacity ideal for families. Includes steamer basket for vegetables. Keep warm function.',
                'short_description': '5L Capacity, Steamer Basket, Keep Warm',
                'price': 3299,
                'compare_price': 4299,
                'stock': 75,
                'specifications': {
                    'Capacity': '5 Liters',
                    'Type': 'Electric Rice Cooker',
                    'Features': 'Keep Warm, Steamer Basket',
                    'Material': 'Non-stick Inner Pot',
                    'Power': '700W'
                }
            },
            
            # Fashion Items
            {
                'name': 'Nike Air Max Men\'s Running Shoes',
                'category': 'Shoes',
                'brand': 'Nike',
                'description': 'Iconic Air Max cushioning for ultimate comfort. Breathable mesh upper with synthetic overlays. Perfect for running and casual wear.',
                'short_description': 'Air Max Cushioning, Breathable, Multiple Sizes',
                'price': 7999,
                'compare_price': 9999,
                'stock': 50,
                'specifications': {
                    'Type': 'Running Shoes',
                    'Material': 'Mesh Upper',
                    'Sole': 'Rubber',
                    'Available Sizes': '40-45',
                    'Colors': 'Black, White, Blue'
                }
            },
            {
                'name': 'Adidas Men\'s Cotton T-Shirt - Pack of 3',
                'category': 'Men\'s Fashion',
                'brand': 'Adidas',
                'description': 'Premium cotton t-shirts perfect for everyday wear. Comfortable fit with iconic Adidas branding. Available in multiple colors.',
                'short_description': 'Pack of 3, 100% Cotton, Comfortable Fit',
                'price': 2499,
                'compare_price': 3499,
                'stock': 90,
                'specifications': {
                    'Material': '100% Cotton',
                    'Pack': '3 T-Shirts',
                    'Sizes': 'M, L, XL, XXL',
                    'Colors': 'Black, White, Grey',
                    'Fit': 'Regular Fit'
                }
            },
            {
                'name': 'Puma Women\'s Sports Bra',
                'category': 'Women\'s Fashion',
                'brand': 'Puma',
                'description': 'High-support sports bra for active women. Moisture-wicking fabric keeps you dry during workouts. Removable padding for customized comfort.',
                'short_description': 'High Support, Moisture-Wicking, Removable Pads',
                'price': 1899,
                'compare_price': 2599,
                'stock': 65,
                'specifications': {
                    'Support': 'High Impact',
                    'Material': 'Polyester/Elastane',
                    'Features': 'Moisture-Wicking',
                    'Sizes': 'S, M, L, XL',
                    'Colors': 'Black, Pink, Blue'
                }
            },
            
            # Health & Beauty
            {
                'name': 'Nivea Body Lotion 400ml',
                'category': 'Health & Beauty',
                'brand': 'Nivea',
                'description': 'Nourishing body lotion for soft, smooth skin. Deep moisture with Vitamin E. Fast absorbing formula. Suitable for all skin types.',
                'short_description': '400ml, Deep Moisture, Vitamin E',
                'price': 899,
                'compare_price': 1199,
                'stock': 150,
                'specifications': {
                    'Size': '400ml',
                    'Type': 'Body Lotion',
                    'Ingredients': 'Vitamin E, Glycerin',
                    'Skin Type': 'All Skin Types',
                    'Scent': 'Mild'
                }
            },
            
            # Tablets
            {
                'name': 'Samsung Galaxy Tab A8 10.5" 64GB',
                'category': 'Tablets',
                'brand': 'Samsung',
                'description': 'Large 10.5" display perfect for entertainment and productivity. Powerful speakers with Dolby Atmos. Long battery life up to 14 hours.',
                'short_description': '10.5" Display, 64GB Storage, Dolby Atmos',
                'price': 28999,
                'compare_price': 34999,
                'stock': 30,
                'specifications': {
                    'Display': '10.5" TFT LCD',
                    'RAM': '4GB',
                    'Storage': '64GB (Expandable)',
                    'Battery': '7040mAh',
                    'OS': 'Android 11',
                    'Camera': '8MP Rear, 5MP Front'
                }
            },
            
            # Sports Equipment
            {
                'name': 'Adjustable Dumbbells Set 20KG',
                'category': 'Sports & Outdoors',
                'brand': 'Generic',
                'description': 'Complete home gym solution. Adjustable weight from 5kg to 20kg per dumbbell. Includes connecting rod to convert to barbell.',
                'short_description': '20KG Set, Adjustable, Barbell Connector',
                'price': 4999,
                'compare_price': 6999,
                'stock': 40,
                'specifications': {
                    'Total Weight': '20KG',
                    'Type': 'Adjustable Dumbbells',
                    'Material': 'Cast Iron',
                    'Includes': 'Connecting Rod',
                    'Plates': 'Multiple Weight Plates'
                }
            },
            {
                'name': 'Yoga Mat 6mm Thick with Carry Bag',
                'category': 'Sports & Outdoors',
                'brand': 'Generic',
                'description': 'Premium yoga mat for comfort during exercise. Non-slip surface, easy to clean. Includes carry bag and strap for portability.',
                'short_description': '6mm Thick, Non-slip, Carry Bag Included',
                'price': 1499,
                'compare_price': 2199,
                'stock': 80,
                'specifications': {
                    'Thickness': '6mm',
                    'Material': 'NBR Foam',
                    'Size': '183cm x 61cm',
                    'Features': 'Non-slip, Waterproof',
                    'Accessories': 'Carry Bag, Strap'
                }
            },
        ]
        
        # Create products
        for product_data in products_data:
            category = Category.objects.filter(name=product_data['category']).first()
            brand = Brand.objects.filter(name=product_data['brand']).first()
            vendor = random.choice(self.vendors)
            
            specifications = product_data.pop('specifications')
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    **product_data,
                    'category': category,
                    'brand': brand,
                    'vendor': vendor,
                    'is_featured': random.choice([True, False]),
                    'weight': random.uniform(0.5, 5.0)
                }
            )
            
            if created:
                # Add specifications
                for i, (spec_name, spec_value) in enumerate(specifications.items()):
                    ProductSpecification.objects.create(
                        product=product,
                        name=spec_name,
                        value=spec_value,
                        order=i
                    )
                
                # Add reviews
                self.create_reviews(product)
        
        self.stdout.write(f'✓ Created {len(products_data)} products with specifications')

    def create_reviews(self, product):
        """Create reviews for a product"""
        reviews_data = [
            {
                'rating': 5,
                'title': 'Excellent product!',
                'comment': 'Very satisfied with this purchase. Quality is top-notch and delivery was fast. Highly recommend!'
            },
            {
                'rating': 4,
                'title': 'Good value for money',
                'comment': 'Works as expected. Good quality for the price. Would buy again.'
            },
            {
                'rating': 5,
                'title': 'Amazing!',
                'comment': 'Exceeded my expectations. Great customer service and fast delivery to Nairobi.'
            },
            {
                'rating': 3,
                'title': 'Decent product',
                'comment': 'It\'s okay. Does the job but nothing exceptional. Delivery took a bit longer than expected.'
            },
        ]
        
        available_users = [u for u in self.users if not u.is_vendor]
        
        for review_data in random.sample(reviews_data, min(3, len(reviews_data))):
            user = random.choice(available_users)
            Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={
                    **review_data,
                    'is_verified_purchase': random.choice([True, False]),
                    'is_approved': True,
                    'helpful_count': random.randint(0, 25)
                }
            )

    def seed_coupons(self):
        """Create discount coupons"""
        self.stdout.write('Seeding coupons...')
        
        coupons_data = [
            {
                'code': 'WELCOME2024',
                'discount_type': 'percentage',
                'discount_value': 10,
                'minimum_purchase': 2000,
                'maximum_discount': 500,
                'usage_limit': 100,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=30)
            },
            {
                'code': 'FLASH500',
                'discount_type': 'fixed',
                'discount_value': 500,
                'minimum_purchase': 5000,
                'usage_limit': 50,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=7)
            },
            {
                'code': 'MEGA20',
                'discount_type': 'percentage',
                'discount_value': 20,
                'minimum_purchase': 10000,
                'maximum_discount': 3000,
                'usage_limit': 200,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=60)
            },
            {
                'code': 'NEWUSER',
                'discount_type': 'percentage',
                'discount_value': 15,
                'minimum_purchase': 1000,
                'maximum_discount': 1000,
                'usage_limit': None,
                'user_limit': 1,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=365)
            },
        ]
        
        for coupon_data in coupons_data:
            Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
        
        self.stdout.write(f'✓ Created {len(coupons_data)} coupons')

    def seed_banners(self):
        """Create homepage banners"""
        self.stdout.write('Seeding banners...')
        
        banners_data = [
            {
                'title': 'Black Friday Mega Sale',
                'subtitle': 'Up to 50% OFF on Electronics',
                'button_text': 'Shop Now',
                'link': '/category/electronics',
                'order': 1,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30)
            },
            {
                'title': 'New Arrivals',
                'subtitle': 'Latest Smartphones from Samsung & Xiaomi',
                'button_text': 'Explore',
                'link': '/category/smartphones',
                'order': 2,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=60)
            },
            {
                'title': 'Home Appliances Sale',
                'subtitle': 'Free Delivery on Orders Above KES 10,000',
                'button_text': 'View Deals',
                'link': '/category/home-kitchen',
                'order': 3,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=45)
            },
        ]
        
        for banner_data in banners_data:
            Banner.objects.get_or_create(
                title=banner_data['title'],
                defaults=banner_data
            )
        
        self.stdout.write(f'✓ Created {len(banners_data)} banners')

    def seed_orders(self):
        """Create sample orders"""
        self.stdout.write('Seeding orders...')
        
        regular_users = [u for u in self.users if not u.is_vendor]
        products = list(Product.objects.all()[:10])
        pickup_stations = list(PickupStation.objects.all()[:3])
        
        for i in range(15):
            user = random.choice(regular_users)
            delivery_method = random.choice(['home_delivery', 'pickup_station'])
            
            # Get address or pickup station
            delivery_address = None
            pickup_station = None
            
            if delivery_method == 'home_delivery':
                delivery_address = user.addresses.filter(is_default=True).first()
                if not delivery_address:
                    delivery_address = user.addresses.first()
                delivery_fee = Decimal('300.00')
            else:
                pickup_station = random.choice(pickup_stations)
                delivery_fee = Decimal('150.00')
            
            # Create order
            subtotal = Decimal('0.00')
            order_items_data = []
            
            # Add 1-4 random products
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price = product.price
                total = price * quantity
                subtotal += total
                
                order_items_data.append({
                    'product': product,
                    'vendor': product.vendor,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'quantity': quantity,
                    'price': price,
                    'total': total
                })
            
            total = subtotal + delivery_fee
            
            # Create order
            order = Order.objects.create(
                user=user,
                status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                delivery_method=delivery_method,
                delivery_address=delivery_address,
                pickup_station=pickup_station,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                tax=Decimal('0.00'),
                discount=Decimal('0.00'),
                total=total,
                customer_note='Please handle with care'
            )
            
            # Create order items
            for item_data in order_items_data:
                OrderItem.objects.create(order=order, **item_data)
            
            # Create payment
            payment_method = random.choice(['mpesa', 'card', 'cash'])
            payment_status = 'completed' if order.status in ['confirmed', 'processing', 'shipped', 'delivered'] else 'pending'
            
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                status=payment_status,
                amount=total
            )
            
            if payment_method == 'mpesa' and payment_status == 'completed':
                payment.mpesa_receipt = f'QAZ{random.randint(1000000, 9999999)}'
                payment.mpesa_phone = user.phone_number
                payment.save()
            elif payment_method == 'card' and payment_status == 'completed':
                payment.card_last4 = str(random.randint(1000, 9999))
                payment.card_brand = random.choice(['Visa', 'Mastercard'])
                payment.save()
        
        self.stdout.write(f'✓ Created 15 sample orders with payments')