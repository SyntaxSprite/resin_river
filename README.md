# resin_river
resin inspired furnishures

# Comprehensive Django Web Development Guide

## Views

### Item Details View (`ItemDetails`):

#### **Purpose:**
Display detailed information about a specific item.

#### **Methods:**
- `get` for rendering the details page.
- `post` for handling form submissions.

#### **Key Points:**
- Use `get_object_or_404` for fetching the item based on slug.
- Implement logic for both "Add to Cart" and "Wish List" actions in the `post` method.
- Redirect back to the item details page after handling actions using `HttpResponseRedirect(request.path)`.

#### **Example:**
```python
class ItemDetails(View):
    def get(self, request, slug):
        post = get_object_or_404(Items, slug=slug)
        context = {'post': post, 'post_tag': post.Tag.all()}
        return render(request, 'item-details.html', context)

    def post(self, request, slug):
        post = get_object_or_404(Items, slug=slug)
        post_id = post.id

        # Handle "Add to Cart" logic
        cart_list = request.session.get('cart_list', [])
        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True

        # Handle "Wish List" logic
        wish_list = request.session.get('wish_list', [])
        if post_id not in wish_list:
            wish_list.append(post_id)
            request.session['wish_list'] = wish_list
            request.session.modified = True

        # Redirect to the item details page after handling both actions
        return HttpResponseRedirect(request.path)
```

### Add to Cart View (`AddToCart`):

#### **Purpose:**
Add items to the user's shopping cart.

#### **Methods:**
- `post` for handling form submissions.

#### **Key Points:**
- Update session data to manage the user's cart.
- Redirect to an appropriate page after adding items (e.g., cart page).

#### **Example:**
```python
class AddToCart(View):
    def post(self, request):
        post_id = request.POST.get('post_id')
        cart_list = request.session.get('cart_list', [])

        if post_id not in cart_list:
            cart_list.append(post_id)
            request.session['cart_list'] = cart_list
            request.session.modified = True

        # Redirect to the cart page after adding items
        return HttpResponseRedirect(reverse('cart'))
```

### Wish List View (`WishList`):

#### **Purpose:**
Manage items in the user's wish list.

#### **Methods:**
- `get` for rendering the wish list.
- `post` for handling form submissions.

#### **Key Points:**
- Update session data to manage the user's wish list.
- Redirect to an appropriate page after managing wish list items.

#### **Example:**
```python
class WishList(View):
    def get(self, request):
        wish_list = request.session.get('wish_list', [])
        context = {}

        if not wish_list:
            context['has_post'] = False
        else:
            posts = Items.objects.filter(id__in=wish_list)
            context['post'] = posts
            context['has_post'] = True

        return render(request, 'wish-list.html', context)

    def post(self, request):
        post_id = request.POST.get('post_id')
        wish_list = request.session.get('wish_list', [])

        if post_id not in wish_list:
            wish_list.append(post_id)
            request.session['wish_list'] = wish_list
            request.session.modified = True

        return HttpResponseRedirect('/')
```

## Models

### `Items` Model:

#### **Attributes:**
- `name`, `description`, `price` for item details.
- `image1`, `image2`, `image3` for multiple images.
- `Tag` for categorization.

#### **Relationships:**
- Use `ForeignKey` and `ManyToManyField` for relationships between items, categories, and tags.

#### **Example:**
```python
class Items(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(upload_to='images/')
    image2 = models.ImageField(upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/', blank=True, null=True)
    Tag = models.ManyToManyField(Tag, blank=True)
    slug = models.SlugField(default="", unique=True, null=True)
    # Add other fields as needed
```

## Templates

### Item Details Template (`item-details.html`):

- Display item details, images, and related information.
- Include forms for "Add to Cart" and "Wish List" actions.

#### **Example:**
```html
<form method="post" action="{% url 'item-details' post.slug %}">
    {% csrf_token %}
    <input type="hidden" name="post

_id" value="{{ post.id }}">
    <button type="submit">Add to Cart</button>
</form>

<form method="post" action="{% url 'item-details' post.slug %}">
    {% csrf_token %}
    <input type="hidden" name="post_id" value="{{ post.id }}">
    <button type="submit">Add to Wish List</button>
</form>
```

## URLs

- Define URL patterns in `urls.py` for each view, including item details, add to cart, and wish list.
- Use reverse URL resolution for redirection.

#### **Example:**
```python
urlpatterns = [
    path('item/<slug:slug>/', ItemDetails.as_view(), name='item-details'),
    path('add-to-cart/', AddToCart.as_view(), name='add-to-cart'),
    path('wish-list/', WishList.as_view(), name='wish-list'),
    # Add other URL patterns as needed
]
```

## General Tips

- **Consistent Indentation:** Maintain consistent indentation for readability.
- **Error Handling:** Use `get_object_or_404` for fetching objects to handle potential errors.
- **Session Management:** Utilize session data for storing temporary user-specific information.
- **Redirects:** After form submissions, redirect users to appropriate pages for a better user experience.
- **Reusable Code:** Create reusable components, such as forms and templates, to enhance maintainability.

This comprehensive guide provides a step-by-step approach with practical examples for implementing key functionalities in a Django web application. It aims to be clear and actionable, serving as a reference for future development.