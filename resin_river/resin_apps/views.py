from django.shortcuts import render, get_object_or_404
from .models import Items
from django.views import View
from django.http import HttpResponseRedirect

# Create your views here.

def startingpage(request):
    latest_posts = Items.objects.all().order_by('created_at')[:3]
    featured_posts = Items.objects.filter(Tag__caption='Featured')

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
        context = {
            'post':post,
            'post_tag': post.Tag.all()
        }
        return render(request, 'resin_apps/item-details.html', context)
    

    class WishList(View):
        def get(self, request):
            wish_list = request.sessions.get('wish_list', [])
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
            wish_list = request.sessions.get('wish_list', [])

            if post_id not in wish_list:
                wish_list.append(post_id)
            request.sessions['wish_list'] = wish_list
            request.sessions.modified = True
            return HttpResponseRedirect('/')

