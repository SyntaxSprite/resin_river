from django.contrib import admin

from.models import Tag, Category, Items

class ItemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'Category',)
    list_filter = ('Category','price','Tag',)
    prepopulated_fields = {'slug':('name',)}



admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Items, ItemsAdmin)

# Register your models here.
