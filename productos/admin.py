from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock', 'disponible', 'fecha_creacion')
    list_filter = ('disponible', 'fecha_creacion')
    search_fields = ('nombre',)
    ordering = ('nombre',)