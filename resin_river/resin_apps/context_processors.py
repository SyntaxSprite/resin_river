from typing import Dict
from django.http import HttpRequest
from .models import Cart, CartItem


def cart_context(request: HttpRequest) -> Dict[str, int]:
    """Provide a cart_count for header badge.

    - Authenticated users: sum of quantities in DB cart
    - Anonymous users: number of ids in session 'cart_list'
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
            session_list = request.session.get('cart_list', [])
            cart_count = len(session_list) if session_list else 0
    except Exception:
        cart_count = 0

    return {"cart_count": cart_count}


