from django.contrib import admin
from .models import Tag, Category, Items, Cart, CartItem, HomeHero, HomePageSection, Testimonial, PaymentMethod, Order, OrderItem, ShippingMethod, TaxConfiguration, DiscountCode, SavedAddress


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('caption',)
    search_fields = ('caption',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'display_order', 'get_item_count')
    list_filter = ('is_featured',)
    search_fields = ('name',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Homepage Display', {
            'fields': ('is_featured', 'display_order', 'featured_image'),
            'description': 'Control how this category appears on the homepage'
        }),
    )
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)
    fields = ('item', 'quantity', 'added_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'get_total_items')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    get_total_items.short_description = 'Total Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'item', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'item__name')
    readonly_fields = ('added_at',)


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'Category', 'is_featured', 'is_on_sale', 'is_latest_arrival', 'available', 'display_order')
    list_filter = ('Category', 'available', 'is_featured', 'is_on_sale', 'is_latest_arrival', 'Tag', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'discount_percentage')
    filter_horizontal = ('Tag',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'Category', 'description', 'price', 'sale_price', 'available')
        }),
        ('Images', {
            'fields': ('image1', 'image2', 'image3')
        }),
        ('Homepage Display', {
            'fields': ('is_featured', 'is_on_sale', 'is_latest_arrival', 'display_order'),
            'description': 'Control where this item appears on the homepage'
        }),
        ('Tags', {
            'fields': ('Tag',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'discount_percentage'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "display_order", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("title", "subtitle")
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'image')
        }),
        ('Call to Action Buttons', {
            'fields': ('cta_text', 'cta_url', 'cta2_text', 'cta2_url'),
            'description': 'Add up to two call-to-action buttons'
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order', 'updated_at')
        }),
    )


@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'is_active', 'display_order', 'created_at')
    list_filter = ('section_type', 'is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Section Information', {
            'fields': ('section_type', 'title', 'subtitle', 'content', 'image')
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_url')
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order', 'created_at', 'updated_at')
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'location', 'rating', 'is_active', 'display_order', 'created_at')
    list_filter = ('rating', 'is_active', 'created_at')
    search_fields = ('customer_name', 'location', 'quote')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'location')
        }),
        ('Testimonial Content', {
            'fields': ('quote', 'rating')
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order', 'created_at')
        }),
    )

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'method_type', 'is_active', 'display_order', 'updated_at')
    list_filter = ('method_type', 'is_active', 'updated_at')
    search_fields = ('display_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('method_type', 'display_name', 'is_active', 'display_order', 'description')
        }),
        ('API Configuration', {
            'fields': ('api_key_public', 'api_key_secret'),
            'description': 'API keys for payment gateway integration. Keep secret keys secure!',
            'classes': ('collapse',)
        }),
        ('Bank Deposit Settings', {
            'fields': ('bank_name', 'account_name', 'account_number', 'bank_instructions'),
            'description': 'Only required for Bank Deposit payment method',
            'classes': ('collapse',)
        }),
        ('Additional Settings', {
            'fields': ('icon_url', 'created_at', 'updated_at')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'item_price', 'quantity', 'subtotal')
    fields = ('item', 'item_name', 'item_price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'guest_email', 'status', 'payment_status', 'discount_code', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'discount_code', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'guest_email', 'delivery_last_name', 'discount_code__code')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'guest_email', 'guest_phone', 'status', 'created_at', 'updated_at')
        }),
        ('Contact Information', {
            'fields': ('contact_email_phone', 'email_news')
        }),
        ('Delivery Address', {
            'fields': (
                'delivery_first_name', 'delivery_last_name', 'delivery_address',
                'delivery_city', 'delivery_state', 'delivery_postal_code',
                'delivery_country', 'delivery_phone'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_same_as_shipping',
                'billing_first_name', 'billing_last_name', 'billing_address',
                'billing_city', 'billing_state', 'billing_postal_code',
                'billing_country', 'billing_phone'
            )
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'payment_transaction_id', 'paid_at')
        }),
        ('Discount Information', {
            'fields': ('discount_code',)
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total')
        }),
        ('Shipping Information', {
            'fields': ('shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item_name', 'quantity', 'item_price', 'subtotal')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__order_number', 'item_name', 'item__name')
    readonly_fields = ('item_name', 'item_price', 'subtotal')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_cost', 'free_shipping_threshold', 'is_active', 'display_order', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'display_order')
        }),
        ('Pricing', {
            'fields': ('base_cost', 'cost_per_item', 'free_shipping_threshold'),
            'description': 'Set base cost and per-item cost. Free shipping threshold is optional.'
        }),
        ('Delivery Information', {
            'fields': ('estimated_days_min', 'estimated_days_max')
        }),
        ('Restrictions', {
            'fields': ('available_countries',),
            'description': 'Comma-separated country codes (e.g., US,CA,MX). Leave blank for all countries.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('country', 'state', 'tax_rate', 'is_active', 'display_order')
    list_filter = ('is_active', 'country', 'created_at')
    search_fields = ('country', 'state')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Location', {
            'fields': ('country', 'state')
        }),
        ('Tax Rate', {
            'fields': ('tax_rate',),
            'description': 'Enter as decimal (e.g., 0.075 for 7.5%)'
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order', 'created_at', 'updated_at')
        }),
    )


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'usage_count', 'usage_limit', 'is_active', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'maximum_discount'),
            'description': 'Maximum discount applies only to percentage discounts.'
        }),
        ('Restrictions', {
            'fields': ('minimum_order_total',),
            'description': 'Minimum order total required to use this code.'
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'usage_count', 'per_user_limit'),
            'description': 'Set limits on how many times the code can be used.'
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until'),
            'description': 'Set when the code is valid. Leave blank for no restrictions.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'address_type', 'city', 'state', 'country', 'is_default', 'is_active', 'created_at')
    list_filter = ('address_type', 'is_default', 'is_active', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'label', 'address', 'city', 'state')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Address Label', {
            'fields': ('label', 'address_type', 'is_default', 'is_active')
        }),
        ('Address Details', {
            'fields': (
                'first_name', 'last_name', 'address',
                'city', 'state', 'postal_code', 'country', 'phone'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register your models here.
