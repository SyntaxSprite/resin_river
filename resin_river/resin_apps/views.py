from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Items, Category, Cart, CartItem, HomeHero
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignupForm, CheckoutForm

# Create your views here.

def startingpage(request):
    all_items = Items.objects.all().order_by('-created_at')
    paginator = Paginator(all_items, 9)
    page_number = request.GET.get('page', 1)
    try:
        latest_posts_page = paginator.page(page_number)
    except PageNotAnInteger:
        latest_posts_page = paginator.page(1)
    except EmptyPage:
        latest_posts_page = paginator.page(paginator.num_pages)

    featured_posts = Items.objects.filter(Tag__caption='Featured').order_by('-created_at')[0:3]
    hero = HomeHero.objects.filter(is_active=True).order_by('-updated_at').first()

    context = {
        'latest_posts_page': latest_posts_page,
        'featured_posts': featured_posts
        , 'hero': hero
    }

    return render (request, 'resin_apps/index.html', context)



class ItemDetails(View):
    def get(self, request, slug):
        post = Items.objects.get(slug=slug)
        related_items = Items.objects.filter(Category=post.Category).exclude(slug=slug)[:3]
        context = {
            'post':post,
            'post_tag': post.Tag.all(),
            'related_items': related_items
        }
        return render(request, 'resin_apps/item-details.html', context)
    
    def post(self, request, slug):
        post = Items.objects.get(slug=slug)
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
            wish_list = request.session.get('wish_list', [])

            if post_id not in wish_list:
                wish_list.append(post_id)
            request.session['wish_list'] = wish_list
            request.session.modified = True
            return HttpResponseRedirect('/')
        
class AddToCart(View):
    def post(self, request):
        post_id = request.POST.get('post_id')
        item = Items.objects.get(id=post_id)
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            # Redirect back to referrer for normal POSTs
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            cart_list = request.session.get('cart_list', [])
            if post_id not in cart_list:
                cart_list.append(post_id)
                request.session['cart_list'] = cart_list
                request.session.modified = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
class CartList(View):
    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            items = cart.items.select_related('item').all()
            posts = [ci.item for ci in items]
            context['posts'] = posts
            context['has_post'] = bool(posts)
        else:
            cart_list = request.session.get('cart_list', [])
            if cart_list is None or not cart_list:
                context['posts'] = []
                context['has_post'] = False
            else:
                posts =  Items.objects.filter(id__in=cart_list)
                context['posts'] = posts
                context['has_post'] = True
        
        return render(request,'resin_apps/cart-list.html', context)
        
    



# @login_required
class Checkout(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('item').all()
        posts = [ci.item for ci in items]
        context['post'] = posts
        subtotal = sum([item.price for item in posts]) if posts else 0
        context['subtotal'] = subtotal
        context['has_post'] = bool(posts)
        context['form'] = CheckoutForm()
        return render(request,'resin_apps/checkout.html', context)

    def post(self, request):
        form = CheckoutForm(request.POST)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('item').all()
        posts = [ci.item for ci in items]
        subtotal = sum([item.price for item in posts]) if posts else 0

        if form.is_valid() and posts:
            # In a future step, create Order and proceed to payment gateway
            request.session['checkout_data'] = form.cleaned_data
            request.session['order_subtotal'] = float(subtotal)
            request.session.modified = True
            return redirect('/checkout')

        context = {
            'post': posts,
            'has_post': bool(posts),
            'subtotal': subtotal,
            'form': form,
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
      
class Payment(LoginRequiredMixin, View):
    def get(self, request):
        checkout_data = request.session.get('checkout_data')
        order_subtotal = request.session.get('order_subtotal')
        if not checkout_data or order_subtotal is None:
            return redirect('/checkout')
        return render(request, 'resin_apps/payment.html', {
            'checkout': checkout_data,
            'subtotal': order_subtotal,
        })

    def post(self, request):
        if 'confirm' in request.POST:
            request.session.pop('cart_list', None)
            request.session.pop('checkout_data', None)
            request.session.pop('order_subtotal', None)
            request.session.modified = True
            return redirect('/')
        return redirect('/payment')
