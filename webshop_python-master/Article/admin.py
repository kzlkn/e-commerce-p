from django.contrib import admin
from .models import Article, Book, ElectronicDevice, Superfood, Supplement

# Register your models here.
admin.site.register(Article)
admin.site.register(ElectronicDevice)
admin.site.register(Supplement)
admin.site.register(Superfood)
admin.site.register(Book)
