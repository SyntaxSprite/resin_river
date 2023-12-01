from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Items
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from .forms import SignupForm

# Create your views here.

def startingpage(request):
    latest_posts = Items.objects.all().order_by('created_at')[:3]
    featured_posts = Items.objects.filter(Tag__caption='Featured')[:3]

    context = {
        'latest_posts': latest_posts,
        'featured_posts': featured_posts
    }

    return render (request, 'resin_apps/index.html', context)


class ItemDetails(View):
    def get(self, request, slug):
        post = Items.objects.get(slug=slug)
        context = {
            'post':post,
            'post_tag': post.Tag.all()
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
        cart_list = request.session.get('cart_list', [])
        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True
        return HttpResponseRedirect(request.path)

    
    
    


# @login_required
class WishList(View):
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
        cart_list = request.session.get('cart_list', [])

        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
        
class CartList(View):
    def get(self, request):
        cart_list = request.session.get('cart_list', [])
        context = {}
        if cart_list is None or not cart_list:
            context['post'] = []
            context['has_post'] = False
        else:
            posts =  Items.objects.filter(id__in=cart_list)
            context['post'] = posts
            context['has_post'] = True
        
        return render(request,'resin_apps/cart-list.html', context)
        
    def post(self, request):
        post_id = request.POST.get('post_id')
        cart_list = request.session.get('cart_list', [])
        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True
        return HttpResponseRedirect(request.path)



# @login_required
class Checkout(View):
    def get(self, request):
        cart_list = request.session.get('cart_list', [])
        context = {}
        if cart_list is None or not cart_list:
            context['post'] = []
            context['has_post'] = False
        else:
            posts =  Items.objects.filter(id__in=cart_list)
            context['post'] = posts
            context['has_post'] = True
        
        return render(request,'resin_apps/checkout.html', context)

    def post(self, request):
        post_id = request.POST.get('post_id')
        cart_list = request.session.get('cart_list', [])
        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True
        return HttpResponseRedirect(request.path)
    

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
      
        
           
