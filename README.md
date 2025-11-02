# Jumia V2 E-Commerce Platform

A full-featured e-commerce platform built with Django, inspired by Jumia, with M-Pesa integration, multiple delivery options, and multi-vendor support.

## 🚀 Developer Information

**Project:** Jumia V2  
**Developer:** Steve Ongera  
**Phone:** 0757790687  
**Email:** steveongera001@gmail.com  
**Version:** 2.0.0

---

## 📋 Features

### 🛍️ Core E-Commerce
- Multi-vendor marketplace
- Product catalog with categories, brands, and variants
- Advanced search and filtering
- Product reviews and ratings
- Wishlist functionality
- Shopping cart with session support

### 💳 Payment Integration
- **M-Pesa** (Daraja API)
- **Credit/Debit Cards**
- **Cash on Delivery**
- Secure payment processing
- Transaction history

### 📦 Delivery Options
- **Home Delivery** - Door-to-door delivery
- **Pickup Stations** - Self-service pickup points
- Region-based delivery fees
- Delivery tracking
- Multiple delivery addresses

### 👥 User Management
- Customer accounts
- Vendor accounts with verification
- Address book management
- Order history
- Notifications system

### 🎯 Additional Features
- Discount coupons
- Homepage banners/sliders
- Product specifications
- Stock management
- SEO-friendly URLs (slugs)
- Admin dashboard

---

## 🛠️ Tech Stack

- **Backend:** Django 4.2+
- **Database:** PostgreSQL / MySQL / SQLite
- **Payment:** M-Pesa Daraja API
- **Frontend:** Django Templates (can be replaced with React/Vue)
- **Admin:** Django Admin (customized)

---

## 📥 Installation

### Prerequisites
```bash
Python 3.8+
pip
virtualenv (recommended)
PostgreSQL/MySQL (for production)
```

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd jumia-v2
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django
pip install pillow  # For image handling
pip install python-decouple  # For environment variables
pip install requests  # For M-Pesa API
pip install psycopg2-binary  # For PostgreSQL (optional)
```

4. **Create .env file**
```bash
touch .env
```

Add the following to your `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# M-Pesa Configuration
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

---

## 📁 Project Structure

```
jumia-v2/
├── manage.py
├── requirements.txt
├── .env
├── README.md
├── jumia_v2/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/
│   ├── models.py           # Database models
│   ├── admin.py            # Admin configuration
│   ├── views.py            # Views/Controllers
│   ├── urls.py             # URL routing
│   ├── forms.py            # Forms
│   ├── serializers.py      # API serializers (if using DRF)
│   └── templates/          # HTML templates
├── payments/
│   ├── mpesa.py           # M-Pesa integration
│   └── card.py            # Card payment integration
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
    ├── products/
    ├── brands/
    ├── categories/
    └── banners/
```

---

## 🗄️ Database Models

### Core Models
- **User** - Extended user with vendor capabilities
- **Product** - Main product model with variants
- **Category** - Hierarchical category structure
- **Brand** - Product brands
- **Vendor** - Multi-vendor support

### Shopping Models
- **Cart** & **CartItem** - Shopping cart
- **Order** & **OrderItem** - Order management
- **Wishlist** - Saved products

### Payment Models
- **Payment** - Payment transactions
- **Coupon** - Discount codes

### Delivery Models
- **Address** - User delivery addresses
- **PickupStation** - Pickup locations
- **DeliveryZone** - Delivery pricing by region

---

## 🔐 Admin Panel

Access the admin panel at `/admin` with superuser credentials.

### Features:
- Product management with inline images and variants
- Order management with status tracking
- Payment monitoring
- User and vendor management
- Inventory tracking
- Coupon management
- Banner/slider management
- Delivery zone configuration

---

## 💰 M-Pesa Integration

### Setup
1. Register for M-Pesa Daraja API at https://developer.safaricom.co.ke
2. Get your Consumer Key and Consumer Secret
3. Add credentials to `.env` file
4. Implement STK Push for payment initiation
5. Set up callback URL for payment confirmation

### Payment Flow
1. User selects M-Pesa payment method
2. System initiates STK Push
3. User enters M-Pesa PIN on phone
4. Payment confirmation received via callback
5. Order status updated automatically

---

## 📦 Deployment

### For Production

1. **Update settings.py**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

2. **Configure database**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jumia_v2_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. **Collect static files**
```bash
python manage.py collectstatic
```

4. **Use production server**
- Gunicorn
- uWSGI
- Apache/Nginx

---

## 🧪 Testing

```bash
python manage.py test
```

---

## 📝 API Documentation

If implementing REST API with Django REST Framework:
- `/api/products/` - Product listing
- `/api/categories/` - Categories
- `/api/cart/` - Cart operations
- `/api/orders/` - Order management
- `/api/payments/` - Payment processing

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

For support and inquiries:

**Steve Ongera**  
📧 Email: steveongera001@gmail.com  
📱 Phone: 0757790687

---

## 🙏 Acknowledgments

- Inspired by Jumia Kenya
- Built with Django
- M-Pesa integration by Safaricom Daraja API

---

## 📋 TODO / Roadmap

- [ ] Implement M-Pesa Daraja API integration
- [ ] Add card payment gateway (Stripe/PayPal)
- [ ] Build frontend templates
- [ ] Create REST API with DRF
- [ ] Add email notifications
- [ ] Implement SMS notifications
- [ ] Add product comparison feature
- [ ] Build mobile app (React Native/Flutter)
- [ ] Add analytics dashboard
- [ ] Implement live chat support
- [ ] Add social media login
- [ ] Multi-language support
- [ ] Currency conversion

---

## 🔄 Version History

### Version 2.0.0 (Current)
- Complete Django models implementation
- Admin panel customization
- Multi-vendor support
- M-Pesa payment structure
- Pickup station system
- Enhanced product management

---

**Built with ❤️ by Steve Ongera**