from django.db import models
import uuid
from django.utils.text import slugify

class Category(models.Model):
    """Product categories with hierarchical support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads/categories/', blank=True, null=True)    
    
    is_active = models.BooleanField(default=True)
    display_order = models.CharField(max_length=10, default="desc")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Set the slug to the name if not set
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def products_count(self):
        return self.products.count()


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

    # Set the slug to the name if not set
    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = self.name
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
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
    image = models.ImageField(upload_to='uploads/products/')
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
        related_name='product_variants'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
