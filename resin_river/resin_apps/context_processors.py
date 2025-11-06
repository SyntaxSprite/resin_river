from typing import Dict
from django.http import HttpRequest
from django.db.models import Q, Count
from .models import Cart, CartItem, Category


def cart_context(request: HttpRequest) -> Dict[str, int]:
    """Provide a cart_count for header badge.

    - Authenticated users: sum of quantities in DB cart
    - Anonymous users: sum of quantities in session 'cart_dict'
    """
    cart_count = 0

    try:
        if request.user.is_authenticated:
            try:
                cart = Cart.objects.select_related('user').prefetch_related('items').get(user=request.user)
                cart_count = sum(ci.quantity for ci in cart.items.all())
            except Cart.DoesNotExist:
                cart_count = 0
        else:
            # Use new cart_dict structure
            cart_dict = request.session.get('cart_dict', {})
            if cart_dict:
                cart_count = sum(cart_dict.values())
            else:
                # Fallback to old cart_list format for migration
                session_list = request.session.get('cart_list', [])
                cart_count = len(session_list) if session_list else 0
    except Exception:
        cart_count = 0

    return {"cart_count": cart_count}


def categories_context(request: HttpRequest) -> Dict:
    """Provide categories for navigation menu."""
    categories = Category.objects.annotate(
        item_count=Count('items', filter=Q(items__available=True))
    ).filter(item_count__gt=0).order_by('display_order', 'name')[:10]  # Limit to 10 for nav
    
    return {"nav_categories": categories}


