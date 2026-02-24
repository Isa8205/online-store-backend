"""
Django E-Commerce Database Schema
==================================
Comprehensive models for an e-commerce application supporting:
- Products & Categories
- User Profiles & Addresses
- Shopping Carts
- Orders & Order Items
- Payment Transactions
- Reviews & Wishlists

Usage:
1. Copy these models to your Django app's models.py
2. Run: python manage.py makemigrations
3. Run: python manage.py migrate
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


# =============================================================================
# USER & AUTHENTICATION MODELS
# =============================================================================

class User(AbstractUser):
    """Extended user model with additional profile fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Security
    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(
        max_length=20,
        choices=[
            ('authenticator', 'Authenticator App'),
            ('sms', 'SMS'),
            ('email', 'Email'),
        ],
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email


class Address(models.Model):
    """User delivery addresses"""
    ADDRESS_TYPES = [
        ('shipping', 'Shipping'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    label = models.CharField(max_length=50)  # e.g., "Home", "Work", "Mom's House"
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='both')
    
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    phone = models.CharField(max_length=20)
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.label} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


# =============================================================================
# PRODUCT & CATEGORY MODELS
# =============================================================================

class Category(models.Model):
    """Product categories with hierarchical support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Hierarchical categories
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Main product model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=150)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True
    )
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Original price before discount"
    )
    cost_per_item = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="For profit calculations"
    )
    
    # Inventory
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    track_quantity = models.BooleanField(default=True)
    
    # Physical properties
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(
        max_length=10,
        choices=[('kg', 'Kilograms'), ('lb', 'Pounds'), ('g', 'Grams'), ('oz', 'Ounces')],
        default='kg'
    )
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price
    
    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        return self.quantity > 0 or not self.track_quantity
    
    @property
    def is_low_stock(self):
        return self.track_quantity and self.quantity <= self.low_stock_threshold


class ProductImage(models.Model):
    """Product images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order']
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Product variants (size, color combinations)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    name = models.CharField(max_length=100)  # e.g., "Small / Red"
    sku = models.CharField(max_length=100, unique=True)
    
    # Variant-specific pricing (optional override)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    quantity = models.PositiveIntegerField(default=0)
    
    # Options
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=50, blank=True, null=True)
    
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='variants'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def effective_price(self):
        return self.price if self.price else self.product.price


class Tag(models.Model):
    """Product tags for filtering and organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        db_table = 'tags'
    
    def __str__(self):
        return self.name


# =============================================================================
# SHOPPING CART MODELS
# =============================================================================

class Cart(models.Model):
    """Shopping cart"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Can be associated with user or session for guest checkout
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Guest Cart {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Items in shopping cart"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # For selected items during checkout
    is_selected = models.BooleanField(default=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        if self.variant:
            return self.variant.effective_price
        return self.product.price
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


# =============================================================================
# ORDER MODELS
# =============================================================================

class Order(models.Model):
    """Customer orders"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True
    )
    email = models.EmailField()  # Store email for guest orders
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Currency
    currency = models.CharField(max_length=3, default='KES')
    
    # Shipping adress
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL
    )
    
    # Notes
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: VIBE-YYYYMMDD-XXXXX
            from django.utils import timezone
            import random
            import string
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            self.order_number = f"{date_str}-{random_str}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual items within an order"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Product snapshot (in case product is deleted/modified)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    # Snapshot data
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=100, blank=True, null=True)
    sku = models.CharField(max_length=100)
    
    # Pricing at time of order
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Product image URL snapshot
    image_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS)
    note = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']


# =============================================================================
# PAYMENT MODELS
# =============================================================================

class PaymentTransaction(models.Model):
    """Payment transactions"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # External payment processor info
    payment_provider = models.CharField(max_length=50)  # e.g., 'stripe', 'paypal'
    provider_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    provider_response = models.JSONField(blank=True, null=True)
    
    # Card info (masked)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    
    # Refund info
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.status}"


# =============================================================================
# COUPON & DISCOUNT MODELS
# =============================================================================

class Coupon(models.Model):
    """Discount coupons"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    maximum_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    usage_limit_per_user = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Restrictions
    applicable_categories = models.ManyToManyField(Category, blank=True)
    applicable_products = models.ManyToManyField(Product, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coupons'
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.times_used < self.usage_limit)
        )


# =============================================================================
# REVIEW & WISHLIST MODELS
# =============================================================================

class Review(models.Model):
    """Product reviews"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Verified purchase order"
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"


class Wishlist(models.Model):
    """User wishlists"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=100, default='My Wishlist')
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    products = models.ManyToManyField(Product, through='WishlistItem')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlists'
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"


class WishlistItem(models.Model):
    """Items in wishlist"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'wishlist_items'
        unique_together = ['wishlist', 'product', 'variant']


# =============================================================================
# ANALYTICS & REPORTING HELPERS
# =============================================================================

class ProductView(models.Model):
    """Track product page views for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    session_key = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_views'
        indexes = [
            models.Index(fields=['product', 'viewed_at']),
            models.Index(fields=['viewed_at']),
        ]


# =============================================================================
# EXAMPLE USAGE & QUERIES
# =============================================================================

"""
Example Queries:
================

# Get all products in a category
products = Product.objects.filter(category__slug='streetwear', status='active')

# Get user's cart with items
cart = Cart.objects.prefetch_related('items__product', 'items__variant').get(user=user)

# Get orders for a user
orders = Order.objects.filter(user=user).prefetch_related('items')

# Get top selling products
from django.db.models import Sum
top_products = Product.objects.annotate(
    total_sold=Sum('orderitem__quantity')
).order_by('-total_sold')[:10]

# Get revenue by category
from django.db.models import F
revenue_by_category = OrderItem.objects.values(
    category_name=F('product__category__name')
).annotate(
    total_revenue=Sum('total_price')
).order_by('-total_revenue')

# Get average rating for products
from django.db.models import Avg
products_with_ratings = Product.objects.annotate(
    avg_rating=Avg('reviews__rating')
)

# Find low stock products
low_stock = Product.objects.filter(
    track_quantity=True,
    quantity__lte=F('low_stock_threshold')
)
"""


print("Django E-Commerce Schema Generated Successfully!")
print("=" * 50)
print("Models included:")
print("- User (extended from AbstractUser)")
print("- Address")
print("- Category (with hierarchy support)")
print("- Product")
print("- ProductImage")
print("- ProductVariant")
print("- Tag")
print("- Cart")
print("- CartItem")
print("- Order")
print("- OrderItem")
print("- OrderStatusHistory")
print("- PaymentTransaction")
print("- Coupon")
print("- Review")
print("- Wishlist")
print("- WishlistItem")
print("- ProductView (for analytics)")
print("=" * 50)
print("Copy this file to your Django app and run migrations!")
