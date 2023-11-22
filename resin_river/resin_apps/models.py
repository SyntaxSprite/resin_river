from django.db import models

# Create your models here.

class Tag(models.Model):
    caption = models.CharField(max_length=100)

    def __str__(self):
        return self.caption
class Category(models.Model):
    name = models.CharField(max_length=200)

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

    def __str__(self):
        return self.name