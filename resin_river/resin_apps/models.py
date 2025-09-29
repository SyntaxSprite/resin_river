from django.db import models
from django.conf import settings

# Create your models here.

class Tag(models.Model):
    caption = models.CharField(max_length=100)

    def __str__(self):
        return self.caption
class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'Categories'


    def __str__(self):
        return self.name

# class Post(models.Model):
#     Category = models.ForeignKey(Category, related_name='posts', on_delete=models.SET_NULL, null= True)
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image1 = models.ImageField(upload_to='images/')
#     image2 = models.ImageField(upload_to='images/', blank=True, null=True)
#     image3 = models.ImageField(upload_to='images/', blank=True, null=True)
#     Tag = models.ManyToManyField(Tag, blank=True)
#     available = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     slug = models.SlugField(default="", unique=True, null=True)
    
#     def __str__(self):
#         return self.name

class Items(models.Model):
    Category = models.ForeignKey(Category, related_name='items', on_delete= models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(upload_to='images/')
    image2 = models.ImageField(upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/', blank=True, null=True)
    Tag = models.ManyToManyField(Tag, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(default="", unique=True, null=True)
    
    class Meta:
        
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.name


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
    cta_text = models.CharField(max_length=100, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Homepage Hero'
        verbose_name_plural = 'Homepage Hero'

    def __str__(self):
        return self.title