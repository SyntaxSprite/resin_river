"""
Django signals for cart migration and other post-login actions
"""
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem, Items


@receiver(user_logged_in)
def migrate_session_cart_to_database(sender, request, user, **kwargs):
    """
    Migrate session cart to database cart when user logs in
    """
    # Get session cart
    cart_dict = request.session.get('cart_dict', {})
    
    # Also check for old cart_list format
    if not cart_dict:
        cart_list = request.session.get('cart_list', [])
        if cart_list:
            # Convert old format to new format
            cart_dict = {}
            for item_id in cart_list:
                item_id_str = str(item_id)
                cart_dict[item_id_str] = cart_dict.get(item_id_str, 0) + 1
    
    if not cart_dict:
        return  # No session cart to migrate
    
    # Get or create user's database cart
    cart, _ = Cart.objects.get_or_create(user=user)
    
    # Migrate items from session to database
    migrated_count = 0
    for item_id_str, quantity in cart_dict.items():
        try:
            item_id = int(item_id_str)
            item = Items.objects.get(id=item_id, available=True)
            
            # Get or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item=item
            )
            
            if created:
                cart_item.quantity = quantity
            else:
                # Add to existing quantity
                cart_item.quantity += quantity
            
            cart_item.save()
            migrated_count += 1
        except (ValueError, Items.DoesNotExist):
            continue  # Skip invalid items
    
    # Clear session cart after migration
    if migrated_count > 0:
        request.session.pop('cart_dict', None)
        request.session.pop('cart_list', None)
        request.session.modified = True

