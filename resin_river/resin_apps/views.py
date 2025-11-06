from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Items, Category, Cart, CartItem, HomeHero, HomePageSection, Testimonial, PaymentMethod, Order, OrderItem, ShippingMethod, TaxConfiguration, DiscountCode, SavedAddress
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.contrib import messages
from django.conf import settings
from django.db.models import Q, Count, Min, Max, Sum
from decimal import Decimal
from .forms import SignupForm, CheckoutForm

# Create your views here.

def startingpage(request):
    # Get active hero (first by display_order, then by updated_at)
    hero = HomeHero.objects.filter(is_active=True).first()
    
    # Get featured categories for collections section
    featured_categories = Category.objects.filter(is_featured=True)[:5]
    
    # Get all items for pagination
    all_items = Items.objects.filter(available=True).order_by('display_order', '-created_at')
    paginator = Paginator(all_items, 12)
    page_number = request.GET.get('page', 1)
    try:
        latest_posts_page = paginator.page(page_number)
    except PageNotAnInteger:
        latest_posts_page = paginator.page(1)
    except EmptyPage:
        latest_posts_page = paginator.page(paginator.num_pages)

    # Get items for Sale tab
    sale_items = Items.objects.filter(is_on_sale=True, available=True).order_by('display_order', '-created_at')
    
    # Get items for Collection tab (featured items)
    collection_items = Items.objects.filter(is_featured=True, available=True).order_by('display_order', '-created_at')
    
    # Get latest arrivals
    latest_arrivals = Items.objects.filter(is_latest_arrival=True, available=True).order_by('display_order', '-created_at')[:2]
    
    # Get promotional banner
    promotional_banner = HomePageSection.objects.filter(
        section_type='promotional', 
        is_active=True
    ).first()
    
    # Get active testimonial
    testimonial = Testimonial.objects.filter(is_active=True).first()

    context = {
        'hero': hero,
        'featured_categories': featured_categories,
        'latest_posts_page': latest_posts_page,
        'sale_items': sale_items,
        'collection_items': collection_items,
        'latest_arrivals': latest_arrivals,
        'promotional_banner': promotional_banner,
        'testimonial': testimonial,
    }

    return render (request, 'resin_apps/index.html', context)



class ItemDetails(View):
    def get(self, request, slug):
        post = get_object_or_404(Items, slug=slug, available=True)
        # Get related items from same category, limit to 4 for "You May Also Like"
        related_items = Items.objects.filter(
            Category=post.Category, 
            available=True
        ).exclude(slug=slug).order_by('display_order', '-created_at')[:4]
        
        # Store in session for recently viewed
        recently_viewed = request.session.get('recently_viewed', [])
        if post.id not in recently_viewed:
            recently_viewed.insert(0, post.id)
            recently_viewed = recently_viewed[:10]  # Keep last 10
            request.session['recently_viewed'] = recently_viewed
            request.session.modified = True
        
        # Get recently viewed items (excluding current)
        recently_viewed_ids = [id for id in recently_viewed if id != post.id][:4]
        recently_viewed_items = Items.objects.filter(
            id__in=recently_viewed_ids,
            available=True
        ).order_by('display_order', '-created_at')
        
        context = {
            'post': post,
            'post_tag': post.Tag.all(),
            'related_items': related_items,
            'recently_viewed_items': recently_viewed_items
        }
        return render(request, 'resin_apps/item-details.html', context)
    
    def post(self, request, slug):
        post = get_object_or_404(Items, slug=slug, available=True)
        post_id = post.id
        wish_list = request.session.get('wish_list', [])
        if post_id not in wish_list:
            wish_list.append(post_id)
            request.session['wish_list'] = wish_list
            request.session.modified = True
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=post)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            cart_list = request.session.get('cart_list', [])
            if post_id not in cart_list:
                cart_list.append(post_id)
                request.session['cart_list'] = cart_list
                request.session.modified = True
        return HttpResponseRedirect(request.path)

    
    
    


# @login_required
class WishList(LoginRequiredMixin, View):
    def get(self, request):
        wish_list = request.session.get('wish_list', [])
        context = {}

        if wish_list is None or not wish_list:
            context['post'] = []
            context['has_post'] = False
        else:
            posts =  Items.objects.filter(id__in=wish_list)
            context['post'] = posts
            context['has_post'] = True

        return render(request,'resin_apps/wish-list.html', context)
        
    def post(self, request):
        post_id = request.POST.get('post_id')
        if not post_id:
            messages.error(request, 'Item ID is required.')
            return HttpResponseRedirect('/')
        
        try:
            item = Items.objects.get(id=post_id, available=True)
        except Items.DoesNotExist:
            messages.error(request, 'Item not found or no longer available.')
            return HttpResponseRedirect('/')
        
        wish_list = request.session.get('wish_list', [])
        if post_id not in wish_list:
            wish_list.append(post_id)
            request.session['wish_list'] = wish_list
            request.session.modified = True
            messages.success(request, f'{item.name} added to wishlist!')
        else:
            messages.info(request, f'{item.name} is already in your wishlist.')
        
        return HttpResponseRedirect('/')
        
class AddToCart(View):
    def post(self, request):
        post_id = request.POST.get('post_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not post_id:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Item ID is required'}, status=400)
            messages.error(request, 'Item ID is required.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        if quantity < 1:
            quantity = 1
        
        try:
            item = Items.objects.get(id=post_id, available=True)
        except Items.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
            messages.error(request, 'Item not found or no longer available.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        if request.user.is_authenticated:
            try:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
                if not created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
            except IntegrityError:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Failed to add item to cart'}, status=500)
                messages.error(request, 'Failed to add item to cart. Please try again.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            
            # Redirect back to referrer for normal POSTs
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, f'{item.name} added to cart!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # For anonymous users, use dict structure: {item_id: quantity}
            cart_dict = request.session.get('cart_dict', {})
            item_id_str = str(post_id)
            if item_id_str in cart_dict:
                cart_dict[item_id_str] += quantity
            else:
                cart_dict[item_id_str] = quantity
            request.session['cart_dict'] = cart_dict
            request.session.modified = True
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, f'{item.name} added to cart!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
class CartList(View):
    def get(self, request):
        context = {}
        cart_items = []
        total = 0
        
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_items_list = cart.items.select_related('item').all()
            for cart_item in cart_items_list:
                item_total = cart_item.item.price * cart_item.quantity
                if cart_item.item.sale_price:
                    item_total = cart_item.item.sale_price * cart_item.quantity
                total += item_total
                cart_items.append({
                    'item': cart_item.item,
                    'quantity': cart_item.quantity,
                    'cart_item_id': cart_item.id,
                    'item_total': item_total
                })
        else:
            cart_dict = request.session.get('cart_dict', {})
            # Migrate old cart_list format to cart_dict if needed
            cart_list = request.session.get('cart_list', [])
            if cart_list and not cart_dict:
                # Convert old list format to dict
                for item_id in cart_list:
                    item_id_str = str(item_id)
                    cart_dict[item_id_str] = cart_dict.get(item_id_str, 0) + 1
                request.session['cart_dict'] = cart_dict
                del request.session['cart_list']
                request.session.modified = True
            
            if cart_dict:
                item_ids = [int(item_id) for item_id in cart_dict.keys()]
                items = Items.objects.filter(id__in=item_ids, available=True)
                for item in items:
                    quantity = cart_dict.get(str(item.id), 0)
                    if quantity > 0:
                        item_total = item.price * quantity
                        if item.sale_price:
                            item_total = item.sale_price * quantity
                        total += item_total
                        cart_items.append({
                            'item': item,
                            'quantity': quantity,
                            'item_id': item.id,
                            'item_total': item_total
                        })
        
        context['cart_items'] = cart_items
        context['total'] = total
        context['has_post'] = bool(cart_items)
        
        return render(request,'resin_apps/cart-list.html', context)
    
    def post(self, request):
        """Handle cart item updates and removals"""
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        cart_item_id = request.POST.get('cart_item_id')
        quantity = request.POST.get('quantity')
        
        if not action:
            messages.error(request, 'Invalid action.')
            return HttpResponseRedirect(request.path)
        
        if request.user.is_authenticated:
            if action == 'remove':
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
                    cart_item.delete()
                    messages.success(request, f'{cart_item.item.name} removed from cart.')
                except CartItem.DoesNotExist:
                    messages.error(request, 'Item not found in cart.')
            elif action == 'update':
                try:
                    cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
                    new_quantity = int(quantity)
                    if new_quantity > 0:
                        cart_item.quantity = new_quantity
                        cart_item.save()
                        messages.success(request, 'Cart updated.')
                    else:
                        cart_item.delete()
                        messages.success(request, f'{cart_item.item.name} removed from cart.')
                except (CartItem.DoesNotExist, ValueError):
                    messages.error(request, 'Failed to update cart.')
        else:
            cart_dict = request.session.get('cart_dict', {})
            item_id_str = str(item_id)
            
            if action == 'remove':
                if item_id_str in cart_dict:
                    del cart_dict[item_id_str]
                    request.session['cart_dict'] = cart_dict
                    request.session.modified = True
                    messages.success(request, 'Item removed from cart.')
            elif action == 'update':
                new_quantity = int(quantity)
                if new_quantity > 0:
                    cart_dict[item_id_str] = new_quantity
                else:
                    if item_id_str in cart_dict:
                        del cart_dict[item_id_str]
                request.session['cart_dict'] = cart_dict
                request.session.modified = True
                messages.success(request, 'Cart updated.')
        
        return HttpResponseRedirect(request.path)


class ShopView(View):
    def get(self, request):
        # Get all categories with item counts
        categories = Category.objects.annotate(
            item_count=Count('items', filter=Q(items__available=True))
        ).filter(item_count__gt=0).order_by('display_order', 'name')
        
        # Get filter parameters
        category_filter = request.GET.get('category', '')
        availability_filter = request.GET.get('availability', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        sort_by = request.GET.get('sort', 'display_order')
        search_query = request.GET.get('search', '')
        
        # Start with all available items
        items = Items.objects.filter(available=True)
        
        # Apply filters
        if category_filter:
            items = items.filter(Category__id=category_filter)
        
        if availability_filter == 'in_stock':
            items = items.filter(available=True)
        elif availability_filter == 'out_of_stock':
            items = items.filter(available=False)
        
        if min_price:
            try:
                items = items.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                items = items.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(Category__name__icontains=search_query)
            )
        
        # Apply sorting
        if sort_by == 'name_asc':
            items = items.order_by('name')
        elif sort_by == 'name_desc':
            items = items.order_by('-name')
        elif sort_by == 'price_asc':
            items = items.order_by('price')
        elif sort_by == 'price_desc':
            items = items.order_by('-price')
        elif sort_by == 'newest':
            items = items.order_by('-created_at')
        else:  # default: display_order
            items = items.order_by('display_order', '-created_at')
        
        # Get price range for filter
        price_range = Items.objects.filter(available=True).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Pagination
        paginator = Paginator(items, 12)  # 12 items per page
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        # Count available items
        in_stock_count = Items.objects.filter(available=True).count()
        out_of_stock_count = Items.objects.filter(available=False).count()
        
        context = {
            'categories': categories,
            'items': page_obj,
            'category_filter': category_filter,
            'availability_filter': availability_filter,
            'min_price': min_price,
            'max_price': max_price,
            'price_range': price_range,
            'sort_by': sort_by,
            'search_query': search_query,
            'in_stock_count': in_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_items': items.count(),
        }
        
        return render(request, 'resin_apps/shop.html', context)


def get_cart_items_and_total(request, shipping_method_id=None, discount_code=None, delivery_country=None, delivery_state=None):
    """Helper function to get cart items and calculate totals for both authenticated and anonymous users"""
    cart_items = []
    subtotal = Decimal('0')
    item_count = 0
    
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items_list = cart.items.select_related('item').all()
        for cart_item in cart_items_list:
            item_total = cart_item.item.price * cart_item.quantity
            if cart_item.item.sale_price:
                item_total = cart_item.item.sale_price * cart_item.quantity
            subtotal += item_total
            item_count += cart_item.quantity
            cart_items.append({
                'item': cart_item.item,
                'quantity': cart_item.quantity,
                'item_total': item_total,
                'cart_item_id': cart_item.id
            })
    else:
        # Anonymous user - get from session
        cart_dict = request.session.get('cart_dict', {})
        if cart_dict:
            item_ids = [int(item_id) for item_id in cart_dict.keys()]
            items = Items.objects.filter(id__in=item_ids, available=True)
            for item in items:
                quantity = cart_dict.get(str(item.id), 0)
                if quantity > 0:
                    item_total = item.price * quantity
                    if item.sale_price:
                        item_total = item.sale_price * quantity
                    subtotal += item_total
                    item_count += quantity
                    cart_items.append({
                        'item': item,
                        'quantity': quantity,
                        'item_total': item_total,
                        'item_id': item.id
                    })
    
    # Calculate shipping
    shipping = Decimal('0')
    shipping_method = None
    if shipping_method_id:
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            shipping = shipping_method.calculate_cost(subtotal, item_count)
        except ShippingMethod.DoesNotExist:
            pass
    
    # If no shipping method selected, use default (first active method)
    if not shipping_method:
        shipping_method = ShippingMethod.objects.filter(is_active=True).order_by('display_order').first()
        if shipping_method:
            shipping = shipping_method.calculate_cost(subtotal, item_count)
    
    # Calculate tax based on delivery location
    tax_rate = Decimal('0')
    estimated_tax = Decimal('0')
    if delivery_country:
        # Try to find tax configuration for country/state
        tax_config = None
        if delivery_state:
            tax_config = TaxConfiguration.objects.filter(
                country__iexact=delivery_country,
                state__iexact=delivery_state,
                is_active=True
            ).first()
        if not tax_config:
            tax_config = TaxConfiguration.objects.filter(
                country__iexact=delivery_country,
                state='',
                is_active=True
            ).first()
        if tax_config:
            tax_rate = tax_config.tax_rate
            estimated_tax = subtotal * tax_rate
    
    # Calculate discount
    discount_amount = Decimal('0')
    applied_discount_code = None
    if discount_code:
        try:
            discount = DiscountCode.objects.get(code__iexact=discount_code.strip())
            is_valid, message = discount.is_valid(user=request.user if request.user.is_authenticated else None, order_total=subtotal)
            if is_valid:
                discount_amount = discount.calculate_discount(subtotal)
                applied_discount_code = discount
        except DiscountCode.DoesNotExist:
            pass
    
    # Calculate total
    total = subtotal + shipping + estimated_tax - discount_amount
    if total < 0:
        total = Decimal('0')
    
    return cart_items, subtotal, shipping, estimated_tax, discount_amount, total, shipping_method, applied_discount_code


class Checkout(View):
    def get(self, request):
        # Get parameters from query string
        shipping_method_id = request.GET.get('shipping_method')
        discount_code = request.GET.get('discount_code')
        delivery_country = request.GET.get('delivery_country')
        delivery_state = request.GET.get('delivery_state')
        
        cart_items, subtotal, shipping, estimated_tax, discount_amount, total, shipping_method, applied_discount = get_cart_items_and_total(
            request, shipping_method_id, discount_code, delivery_country, delivery_state
        )
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart-list')
        
        # Get active payment methods
        payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('display_order', 'method_type')
        
        # Get active shipping methods and calculate costs
        shipping_methods = ShippingMethod.objects.filter(is_active=True).order_by('display_order', 'name')
        item_count = sum(item['quantity'] for item in cart_items)
        
        # Calculate shipping cost for each method
        shipping_methods_with_costs = []
        for method in shipping_methods:
            method_cost = method.calculate_cost(subtotal, item_count)
            shipping_methods_with_costs.append({
                'method': method,
                'cost': method_cost
            })
        
        # Get saved addresses for authenticated users
        saved_addresses = []
        default_address = None
        if request.user.is_authenticated:
            saved_addresses = SavedAddress.objects.filter(user=request.user, is_active=True).order_by('-is_default', '-created_at')
            default_address = saved_addresses.filter(is_default=True).first()
        
        form = CheckoutForm(payment_methods=payment_methods)
        
        # Pre-fill form with default address if available
        if default_address:
            form.fields['delivery_first_name'].initial = default_address.first_name
            form.fields['delivery_last_name'].initial = default_address.last_name
            form.fields['delivery_address'].initial = default_address.address
            form.fields['delivery_city'].initial = default_address.city
            form.fields['delivery_state'].initial = default_address.state
            form.fields['delivery_postal_code'].initial = default_address.postal_code
            form.fields['delivery_country'].initial = default_address.country
            form.fields['delivery_phone'].initial = default_address.phone
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'estimated_tax': estimated_tax,
            'discount_amount': discount_amount,
            'total': total,
            'has_post': bool(cart_items),
            'form': form,
            'payment_methods': payment_methods,
            'shipping_methods': shipping_methods_with_costs,
            'selected_shipping_method': shipping_method,
            'applied_discount': applied_discount,
            'discount_code': discount_code,
            'saved_addresses': saved_addresses,
            'default_address': default_address,
        }
        return render(request,'resin_apps/checkout.html', context)

    def post(self, request):
        # Handle discount code application (AJAX request)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            discount_code = request.POST.get('discount_code', '').strip()
            delivery_country = request.POST.get('delivery_country', '')
            delivery_state = request.POST.get('delivery_state', '')
            shipping_method_id = request.POST.get('shipping_method')
            
            cart_items, subtotal, shipping, estimated_tax, discount_amount, total, shipping_method, applied_discount = get_cart_items_and_total(
                request, shipping_method_id, discount_code, delivery_country, delivery_state
            )
            
            if applied_discount:
                return JsonResponse({
                    'success': True,
                    'discount_amount': float(discount_amount),
                    'subtotal': float(subtotal),
                    'shipping': float(shipping),
                    'tax': float(estimated_tax),
                    'total': float(total),
                    'message': f'Discount code "{applied_discount.code}" applied successfully!'
                })
            else:
                # Try to get the error message from validation
                if discount_code:
                    try:
                        discount = DiscountCode.objects.get(code__iexact=discount_code.strip())
                        is_valid, error_message = discount.is_valid(user=request.user if request.user.is_authenticated else None, order_total=subtotal)
                        if not is_valid:
                            return JsonResponse({
                                'success': False,
                                'message': error_message
                            }, status=400)
                    except DiscountCode.DoesNotExist:
                        pass
                
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid or expired discount code.'
                }, status=400)
        
        form = CheckoutForm(request.POST)
        delivery_country = request.POST.get('delivery_country', '')
        delivery_state = request.POST.get('delivery_state', '')
        shipping_method_id = request.POST.get('shipping_method')
        # Get discount code from POST data (regular field, hidden field, or URL query parameters)
        discount_code = (
            request.POST.get('discount_code', '').strip() or 
            request.POST.get('applied_discount_code', '').strip() or 
            request.GET.get('discount_code', '').strip()
        )
        
        cart_items, subtotal, shipping, estimated_tax, discount_amount, total, shipping_method, applied_discount = get_cart_items_and_total(
            request, shipping_method_id, discount_code, delivery_country, delivery_state
        )
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart-list')
        
        # Get active payment methods
        payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('display_order', 'method_type')
        shipping_methods_list = ShippingMethod.objects.filter(is_active=True).order_by('display_order', 'name')
        item_count = sum(item['quantity'] for item in cart_items)
        
        # Calculate shipping cost for each method
        shipping_methods = []
        for method in shipping_methods_list:
            method_cost = method.calculate_cost(subtotal, item_count)
            shipping_methods.append({
                'method': method,
                'cost': method_cost
            })
        
        form = CheckoutForm(request.POST, payment_methods=payment_methods)
        
        if form.is_valid() and cart_items:
            # Get selected payment method
            payment_method_id = form.cleaned_data.get('payment_method')
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
            except PaymentMethod.DoesNotExist:
                messages.error(request, 'Invalid payment method selected.')
                context = {
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'shipping': shipping,
                    'estimated_tax': estimated_tax,
                    'total': total,
                    'has_post': bool(cart_items),
                    'form': form,
                    'payment_methods': payment_methods,
                }
                return render(request, 'resin_apps/checkout.html', context)
            
            # Create order
            order_data = form.cleaned_data.copy()
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                guest_email=order_data.get('contact_email_phone') if '@' in order_data.get('contact_email_phone', '') else '',
                guest_phone=order_data.get('delivery_phone', ''),
                contact_email_phone=order_data.get('contact_email_phone', ''),
                email_news=order_data.get('email_news', False),
                delivery_first_name=order_data.get('delivery_first_name', ''),
                delivery_last_name=order_data.get('delivery_last_name', ''),
                delivery_address=order_data.get('delivery_address', ''),
                delivery_city=order_data.get('delivery_city', ''),
                delivery_state=order_data.get('delivery_state', ''),
                delivery_postal_code=order_data.get('delivery_postal_code', ''),
                delivery_country=order_data.get('delivery_country', ''),
                delivery_phone=order_data.get('delivery_phone', ''),
                billing_same_as_shipping=order_data.get('billing_same_as_shipping', True),
                billing_first_name=order_data.get('billing_first_name', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_first_name', ''),
                billing_last_name=order_data.get('billing_last_name', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_last_name', ''),
                billing_address=order_data.get('billing_address', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_address', ''),
                billing_city=order_data.get('billing_city', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_city', ''),
                billing_state=order_data.get('billing_state', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_state', ''),
                billing_postal_code=order_data.get('billing_postal_code', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_postal_code', ''),
                billing_country=order_data.get('billing_country', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_country', ''),
                billing_phone=order_data.get('billing_phone', '') if not order_data.get('billing_same_as_shipping', True) else order_data.get('delivery_phone', ''),
                payment_method=payment_method,
                discount_code=applied_discount if applied_discount else None,
                subtotal=subtotal,
                shipping_cost=shipping,
                tax_amount=estimated_tax,
                discount_amount=discount_amount,
                total=total,
                status='pending',
            )
            
            # Increment discount code usage if applied
            if applied_discount:
                # Use select_for_update to prevent race conditions
                from django.db import transaction
                with transaction.atomic():
                    discount = DiscountCode.objects.select_for_update().get(id=applied_discount.id)
                    discount.usage_count += 1
                    discount.save(update_fields=['usage_count'])
                    # Log for debugging
                    print(f"Discount code {discount.code} usage count incremented to {discount.usage_count}")
            elif discount_code:
                # Try to get and increment even if not in applied_discount (fallback)
                try:
                    from django.db import transaction
                    with transaction.atomic():
                        discount = DiscountCode.objects.select_for_update().get(code__iexact=discount_code.strip())
                        discount.usage_count += 1
                        discount.save(update_fields=['usage_count'])
                        # Update order with discount code
                        order.discount_code = discount
                        order.save(update_fields=['discount_code'])
                        print(f"Discount code {discount.code} usage count incremented to {discount.usage_count} (fallback)")
                except DiscountCode.DoesNotExist:
                    pass
            
            # Create order items
            for cart_item_data in cart_items:
                item = cart_item_data['item']
                quantity = cart_item_data['quantity']
                item_price = item.sale_price if item.sale_price else item.price
                
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    item_name=item.name,
                    item_price=item_price,
                    quantity=quantity,
                    subtotal=cart_item_data['item_total']
                )
            
            # Clear cart after order creation
            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart.items.all().delete()
            else:
                request.session['cart_dict'] = {}
                request.session.modified = True
            
            # Store order ID in session for payment page
            request.session['order_id'] = order.id
            request.session.modified = True
            
            # Send order confirmation email
            try:
                from .email_utils import send_order_confirmation_email
                send_order_confirmation_email(order)
            except Exception as e:
                print(f"Error sending order confirmation email: {e}")
                # Don't fail the order creation if email fails
            
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('payment', order_id=order.id)

        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'estimated_tax': estimated_tax,
            'discount_amount': discount_amount,
            'total': total,
            'has_post': bool(cart_items),
            'form': form,
            'payment_methods': payment_methods,
            'shipping_methods': shipping_methods,
            'selected_shipping_method': shipping_method,
            'applied_discount': applied_discount,
            'discount_code': discount_code,
        }
        return render(request, 'resin_apps/checkout.html', context)
    

def signup(request):
       
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        else:
            # Print form errors to the console for debugging
            print(form.errors)
    else:
        form = SignupForm()

    return render(request, 'resin_apps/signup.html', {
        'form': form
    })
      
class Payment(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Verify order belongs to user (if authenticated) or session
        if request.user.is_authenticated:
            if order.user and order.user != request.user:
                messages.error(request, 'You do not have permission to view this order.')
                return redirect('index')
        else:
            # For guest orders, verify via session
            session_order_id = request.session.get('order_id')
            if session_order_id != order.id:
                messages.error(request, 'Invalid order access.')
                return redirect('index')
        
        # Don't allow payment if already paid
        if order.payment_status == 'paid':
            messages.info(request, 'This order has already been paid.')
            return redirect('order-confirmation', order_id=order.id)
        
        context = {
            'order': order,
            'payment_method': order.payment_method,
        }
        return render(request, 'resin_apps/payment.html', context)

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Verify order access
        if request.user.is_authenticated:
            if order.user and order.user != request.user:
                messages.error(request, 'You do not have permission to access this order.')
                return redirect('index')
        else:
            session_order_id = request.session.get('order_id')
            if session_order_id != order.id:
                messages.error(request, 'Invalid order access.')
                return redirect('index')
        
        # Handle payment confirmation (mock for now - will integrate with payment gateway)
        action = request.POST.get('action')
        
        if action == 'confirm_payment':
            # TODO: Integrate with actual payment gateway (Paystack/Stripe)
            # For now, mark as paid (mock)
            order.payment_status = 'paid'
            order.status = 'processing'
            from django.utils import timezone
            order.paid_at = timezone.now()
            order.save()
            
            # Send payment confirmation email
            try:
                from .email_utils import send_payment_confirmation_email
                send_payment_confirmation_email(order)
            except Exception as e:
                print(f"Error sending payment confirmation email: {e}")
                # Don't fail the payment if email fails
            
            messages.success(request, f'Payment confirmed for order {order.order_number}!')
            return redirect('order-confirmation', order_id=order.id)
        elif action == 'cancel':
            order.status = 'cancelled'
            order.save()
            messages.info(request, 'Order cancelled.')
            return redirect('index')
        
        return redirect('payment', order_id=order.id)


class OrderConfirmation(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Verify order access
        if request.user.is_authenticated:
            if order.user and order.user != request.user:
                messages.error(request, 'You do not have permission to view this order.')
                return redirect('index')
        else:
            session_order_id = request.session.get('order_id')
            if session_order_id != order.id:
                messages.error(request, 'Invalid order access.')
                return redirect('index')
        
        context = {
            'order': order,
        }
        return render(request, 'resin_apps/order-confirmation.html', context)


class OrderHistory(LoginRequiredMixin, View):
    """View to display user's order history"""
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(orders, 10)  # 10 orders per page
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        context = {
            'orders': page_obj,
        }
        return render(request, 'resin_apps/order-history.html', context)


class OrderDetail(LoginRequiredMixin, View):
    """View to display individual order details"""
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        context = {
            'order': order,
        }
        return render(request, 'resin_apps/order-detail.html', context)


class UserDashboard(LoginRequiredMixin, View):
    """User dashboard/profile page"""
    def get(self, request):
        # Get user's recent orders
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # Get order statistics
        total_orders = Order.objects.filter(user=request.user).count()
        total_spent = Order.objects.filter(user=request.user, payment_status='paid').aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        # Get pending orders
        pending_orders = Order.objects.filter(
            user=request.user,
            status__in=['pending', 'processing']
        ).count()
        
        context = {
            'user': request.user,
            'recent_orders': recent_orders,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'pending_orders': pending_orders,
        }
        return render(request, 'resin_apps/user-dashboard.html', context)


class UserProfileEdit(LoginRequiredMixin, View):
    """View to edit user profile"""
    def get(self, request):
        context = {
            'user': request.user,
        }
        return render(request, 'resin_apps/user-profile-edit.html', context)
    
    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Update user fields
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email and email != user.email:
            # Check if email is already taken
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('user-profile-edit')
            user.email = email
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user-dashboard')


class SavedAddressesList(LoginRequiredMixin, View):
    """View to list user's saved addresses"""
    def get(self, request):
        addresses = SavedAddress.objects.filter(user=request.user, is_active=True).order_by('-is_default', '-created_at')
        
        context = {
            'addresses': addresses,
        }
        return render(request, 'resin_apps/saved-addresses.html', context)


class SavedAddressAdd(LoginRequiredMixin, View):
    """View to add a new saved address"""
    def get(self, request):
        return render(request, 'resin_apps/saved-address-form.html', {'form_type': 'add'})
    
    def post(self, request):
        label = request.POST.get('label', '').strip()
        address_type = request.POST.get('address_type', 'home')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', '').strip()
        phone = request.POST.get('phone', '').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        if not all([label, first_name, last_name, address, city, state, country, phone]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('saved-address-add')
        
        SavedAddress.objects.create(
            user=request.user,
            label=label,
            address_type=address_type,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            phone=phone,
            is_default=is_default,
        )
        
        messages.success(request, 'Address saved successfully!')
        return redirect('saved-addresses')


class SavedAddressEdit(LoginRequiredMixin, View):
    """View to edit a saved address"""
    def get(self, request, address_id):
        address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
        context = {
            'address': address,
            'form_type': 'edit',
        }
        return render(request, 'resin_apps/saved-address-form.html', context)
    
    def post(self, request, address_id):
        address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
        
        address.label = request.POST.get('label', '').strip()
        address.address_type = request.POST.get('address_type', 'home')
        address.first_name = request.POST.get('first_name', '').strip()
        address.last_name = request.POST.get('last_name', '').strip()
        address.address = request.POST.get('address', '').strip()
        address.city = request.POST.get('city', '').strip()
        address.state = request.POST.get('state', '').strip()
        address.postal_code = request.POST.get('postal_code', '').strip()
        address.country = request.POST.get('country', '').strip()
        address.phone = request.POST.get('phone', '').strip()
        address.is_default = request.POST.get('is_default') == 'on'
        
        if not all([address.label, address.first_name, address.last_name, address.address, address.city, address.state, address.country, address.phone]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('saved-address-edit', address_id=address.id)
        
        address.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('saved-addresses')


class SavedAddressDelete(LoginRequiredMixin, View):
    """View to delete a saved address"""
    def post(self, request, address_id):
        address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
        address.is_active = False
        address.save()
        messages.success(request, 'Address deleted successfully!')
        return redirect('saved-addresses')


# Custom Error Handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


def robots_txt(request):
    """Generate robots.txt file"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /checkout",
        "Disallow: /payment",
        "Disallow: /cart-list",
        "Disallow: /wish-list",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
