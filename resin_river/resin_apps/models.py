from django.db import models
from django.conf import settings

# Create your models here.

class Tag(models.Model):
    caption = models.CharField(max_length=100)

    def __str__(self):
        return self.caption
class Category(models.Model):
    name = models.CharField(max_length=200)
    is_featured = models.BooleanField(default=False, help_text="Show in homepage collections section")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which categories appear (lower numbers first)")
    featured_image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Optional: Custom image for homepage display")
    description = models.TextField(blank=True, help_text="Description for homepage collections section")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Items(models.Model):
    Category = models.ForeignKey(Category, related_name='items', on_delete= models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="If set, item will appear in Sale section")
    image1 = models.ImageField(upload_to='images/')
    image2 = models.ImageField(upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/', blank=True, null=True)
    Tag = models.ManyToManyField(Tag, blank=True)
    available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show in featured/collection section")
    is_on_sale = models.BooleanField(default=False, help_text="Show in Sale tab")
    is_latest_arrival = models.BooleanField(default=False, help_text="Show in Latest Arrivals section")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in product listings (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(default="", unique=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Items'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.sale_price and self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return None


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'item')

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class HomeHero(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to='hero/')
    cta_text = models.CharField(max_length=100, blank=True, help_text="First button text (e.g., 'SHOP NOW')")
    cta_url = models.CharField(max_length=255, blank=True, help_text="First button URL")
    cta2_text = models.CharField(max_length=100, blank=True, help_text="Second button text (e.g., '5% OFF')")
    cta2_url = models.CharField(max_length=255, blank=True, help_text="Second button URL")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0, help_text="If multiple heroes, lower numbers appear first")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Homepage Hero'
        verbose_name_plural = 'Homepage Heroes'
        ordering = ['display_order', '-updated_at']

    def __str__(self):
        return self.title


class HomePageSection(models.Model):
    """Model to manage homepage sections like promotional banners"""
    SECTION_CHOICES = [
        ('promotional', 'Promotional Banner'),
        ('testimonial', 'Testimonial'),
        ('newsletter', 'Newsletter'),
    ]
    
    section_type = models.CharField(max_length=20, choices=SECTION_CHOICES)
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Additional content or description")
    image = models.ImageField(upload_to='sections/', blank=True, null=True)
    cta_text = models.CharField(max_length=100, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Homepage Section'
        verbose_name_plural = 'Homepage Sections'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"


class Testimonial(models.Model):
    """Model for customer testimonials"""
    customer_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    quote = models.TextField()
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"


class PaymentMethod(models.Model):
    """Model for configurable payment methods"""
    METHOD_CHOICES = [
        ('paystack', 'Paystack'),
        ('stripe', 'Stripe'),
        ('bank_deposit', 'Bank Deposit'),
    ]
    
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES, unique=True)
    is_active = models.BooleanField(default=True, help_text="Show this payment method in checkout")
    display_name = models.CharField(max_length=100, help_text="Display name for this payment method")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which methods appear (lower numbers first)")
    
    # API Keys/Configuration (encrypted in production)
    api_key_public = models.CharField(max_length=255, blank=True, help_text="Public API key (e.g., Paystack public key, Stripe publishable key)")
    api_key_secret = models.CharField(max_length=255, blank=True, help_text="Secret API key (keep secure!)")
    
    # Bank Deposit specific fields
    bank_name = models.CharField(max_length=200, blank=True, help_text="Bank name for bank deposit")
    account_name = models.CharField(max_length=200, blank=True, help_text="Account name for bank deposit")
    account_number = models.CharField(max_length=50, blank=True, help_text="Account number for bank deposit")
    bank_instructions = models.TextField(blank=True, help_text="Instructions for bank deposit payment")
    
    # Additional settings
    description = models.TextField(blank=True, help_text="Description shown to customers")
    icon_url = models.URLField(blank=True, help_text="URL to payment method icon/logo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'method_type']
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
    
    def __str__(self):
        return f"{self.get_method_type_display()} - {self.display_name}"


class Order(models.Model):
    """Model to store completed orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Order identification
    order_number = models.CharField(max_length=50, unique=True, help_text="Unique order number")
    
    # User information (nullable for guest checkout)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    guest_email = models.EmailField(blank=True, help_text="Email for guest orders")
    guest_phone = models.CharField(max_length=30, blank=True, help_text="Phone for guest orders")
    
    # Contact information
    contact_email_phone = models.CharField(max_length=255)
    email_news = models.BooleanField(default=False)
    
    # Delivery address
    delivery_first_name = models.CharField(max_length=100, blank=True)
    delivery_last_name = models.CharField(max_length=100)
    delivery_address = models.CharField(max_length=255)
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=30)
    
    # Billing address
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_first_name = models.CharField(max_length=100, blank=True)
    billing_last_name = models.CharField(max_length=100, blank=True)
    billing_address = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_phone = models.CharField(max_length=30, blank=True)
    
    # Payment information
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name='orders')
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    payment_transaction_id = models.CharField(max_length=255, blank=True, help_text="Transaction ID from payment gateway")
    
    # Discount information
    discount_code = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', help_text="Discount code used for this order")
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Order status
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, help_text="Internal notes about the order")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            prefix = "RR"
            random_part = ''.join(random.choices(string.digits, k=8))
            self.order_number = f"{prefix}{random_part}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Model to store individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Items, on_delete=models.SET_NULL, null=True, related_name='order_items')
    item_name = models.CharField(max_length=200, help_text="Store item name at time of order")
    item_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of order")
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="item_price * quantity")
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.item_name} x {self.quantity} - Order {self.order.order_number}"


class ShippingMethod(models.Model):
    """Model for configurable shipping methods"""
    name = models.CharField(max_length=100, help_text="Shipping method name (e.g., 'Standard Shipping', 'Express')")
    description = models.TextField(blank=True, help_text="Description shown to customers")
    is_active = models.BooleanField(default=True, help_text="Show this shipping method in checkout")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which methods appear (lower numbers first)")
    
    # Pricing
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Base shipping cost")
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Order total threshold for free shipping (leave blank if not applicable)")
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Additional cost per item")
    
    # Delivery time
    estimated_days_min = models.PositiveIntegerField(default=3, help_text="Minimum estimated delivery days")
    estimated_days_max = models.PositiveIntegerField(default=7, help_text="Maximum estimated delivery days")
    
    # Restrictions
    available_countries = models.TextField(blank=True, help_text="Comma-separated list of country codes (leave blank for all countries)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
    
    def __str__(self):
        return self.name
    
    def calculate_cost(self, order_total, item_count):
        """Calculate shipping cost based on order total and item count"""
        from decimal import Decimal
        if self.free_shipping_threshold and order_total >= self.free_shipping_threshold:
            return Decimal('0')
        return self.base_cost + (self.cost_per_item * Decimal(str(item_count)))


class TaxConfiguration(models.Model):
    """Model for configurable tax rates by location"""
    country = models.CharField(max_length=100, help_text="Country name or code")
    state = models.CharField(max_length=100, blank=True, help_text="State/province (leave blank for country-wide rate)")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="Tax rate as decimal (e.g., 0.075 for 7.5%)")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['country', 'state', 'display_order']
        verbose_name = 'Tax Configuration'
        verbose_name_plural = 'Tax Configurations'
        unique_together = ('country', 'state')
    
    def __str__(self):
        if self.state:
            return f"{self.country}, {self.state} - {self.tax_rate * 100}%"
        return f"{self.country} - {self.tax_rate * 100}%"


class DiscountCode(models.Model):
    """Model for discount codes/coupons"""
    code = models.CharField(max_length=50, unique=True, help_text="Discount code (e.g., 'SAVE10')")
    description = models.CharField(max_length=200, blank=True, help_text="Description shown to customers")
    
    # Discount type
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount amount (percentage or fixed)")
    
    # Restrictions
    minimum_order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum order total required")
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum discount amount (for percentage discounts)")
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total number of times this code can be used (leave blank for unlimited)")
    usage_count = models.PositiveIntegerField(default=0, help_text="Number of times this code has been used")
    per_user_limit = models.PositiveIntegerField(default=1, help_text="Number of times a single user can use this code")
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True, help_text="Code valid from this date (leave blank for no start date)")
    valid_until = models.DateTimeField(null=True, blank=True, help_text="Code valid until this date (leave blank for no expiry)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Discount Code'
        verbose_name_plural = 'Discount Codes'
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"
    
    def is_valid(self, user=None, order_total=None):
        """Check if discount code is valid"""
        if not self.is_active:
            return False, "This discount code is not active."
        
        # Check date validity
        from django.utils import timezone
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False, "This discount code is not yet valid."
        if self.valid_until and now > self.valid_until:
            return False, "This discount code has expired."
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "This discount code has reached its usage limit."
        
        # Check minimum order total
        if self.minimum_order_total and order_total and order_total < self.minimum_order_total:
            return False, f"Minimum order total of ${self.minimum_order_total} required for this code."
        
        return True, "Valid"
    
    def calculate_discount(self, order_total):
        """Calculate discount amount for given order total"""
        from decimal import Decimal
        if self.discount_type == 'percentage':
            discount = order_total * (self.discount_value / Decimal('100'))
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # fixed
            discount = min(self.discount_value, order_total)
        return discount


class SavedAddress(models.Model):
    """Model for saving user delivery addresses"""
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='home')
    label = models.CharField(max_length=100, help_text="Custom label (e.g., 'My Home', 'Office')")
    
    # Address fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    
    # Settings
    is_default = models.BooleanField(default=False, help_text="Set as default address for checkout")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Saved Address'
        verbose_name_plural = 'Saved Addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset other default addresses for this user
        if self.is_default:
            SavedAddress.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)