import os
import io
import csv
from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import Producto
from .serializers import ProductoSerializer
from .forms import ProductoForm

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Selecciona un archivo CSV")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'categoria', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre',)
    change_list_template = "admin/productos_change_list.html"
    actions = ['cargar_csv_action']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('importar-csv/', self.admin_site.admin_view(self.importar_csv), name='producto_importar_csv'),
        ]
        return custom_urls + urls
    
    def importar_csv(self, request):
        """Vista para importar productos desde CSV"""
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'El archivo debe tener extensión .csv')
                    return redirect('.')
                
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string, None)  # Omitir encabezados
                
                contador = 0
                errores = 0
                
                for row in csv.reader(io_string, delimiter=','):
                    if row and len(row) >= 3:
                        try:
                            Producto.objects.create(
                                nombre=row[0].strip(),
                                precio=row[1].strip(),
                                categoria=row[2].strip().upper(),
                                disponible=True
                            )
                            contador += 1
                        except Exception as e:
                            errores += 1
                            messages.warning(request, f'Error en fila: {e}')
                
                messages.success(request, f'✅ Se cargaron {contador} productos correctamente!')
                if errores > 0:
                    messages.warning(request, f'⚠️ {errores} filas tuvieron errores')
                return redirect('..')
        else:
            form = CsvImportForm()
        
        context = {
            'form': form,
            'title': 'Importar Productos (CSV)',
            'site_header': admin.site.site_header,
            'opts': self.model._meta,
            'add': True,
            'change': False,
        }
        return render(request, "admin/productos_import_csv.html", context)