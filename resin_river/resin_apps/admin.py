from django.contrib import admin

from .models import Tag, Category, Items, Cart, CartItem, HomeHero

class ItemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'Category',)
    list_filter = ('Category','price','Tag',)
    prepopulated_fields = {'slug':('name',)}



@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")


admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Items, ItemsAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)

# Register your models here.
