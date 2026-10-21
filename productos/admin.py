import os
import io
import csv
from django.contrib import admin
from django import forms
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import Producto, Categoria
from .serializers import ProductoSerializer
from .forms import ProductoForm

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Selecciona un archivo CSV")

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'disponible')
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
        """Importa productos desde CSV: nombre, categoria, descripcion"""
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                if not csv_file.name.lower().endswith('.csv'):
                    messages.error(request, 'El archivo debe tener extensión .csv')
                    return redirect('.')

                # Acepta UTF-8 (Google Sheets) y ANSI (Excel)
                contenido = csv_file.read()
                try:
                    texto = contenido.decode('utf-8-sig')
                except UnicodeDecodeError:
                    texto = contenido.decode('latin-1')

                reader = csv.reader(io.StringIO(texto))
                next(reader, None)  # Omitir encabezados

                existentes = {n.upper() for n in Producto.objects.values_list('nombre', flat=True)}
                categorias = {c.nombre: c for c in Categoria.objects.all()}

                cargados = 0
                omitidos, errores, nuevas_cat = [], [], []

                for num, row in enumerate(reader, start=2):
                    if not row or not row[0].strip():
                        continue  # fila vacía
                    if len(row) < 3:
                        errores.append(f'Fila {num}: faltan columnas')
                        continue

                    nombre = row[0].strip().upper()
                    if nombre in existentes:
                        omitidos.append(nombre)
                        continue

                    categoria = None
                    nombre_cat = row[1].strip().upper()
                    if nombre_cat:
                        categoria = categorias.get(nombre_cat)
                        if not categoria:
                            categoria = Categoria.objects.create(nombre=nombre_cat)
                            categorias[nombre_cat] = categoria
                            nuevas_cat.append(nombre_cat)

                    try:
                        with transaction.atomic():
                            Producto.objects.create(
                                nombre=nombre,
                                categoria=categoria,
                                descripcion=row[2].strip(),
                            )
                        existentes.add(nombre)
                        cargados += 1
                    except Exception as e:
                        errores.append(f'Fila {num} ({nombre}): {e}')

                # Resumen
                messages.success(request, f'✅ {cargados} productos cargados.')
                if omitidos:
                    lista = ', '.join(omitidos[:10]) + ('...' if len(omitidos) > 10 else '')
                    messages.info(request, f'⏭️ {len(omitidos)} ya existían y se omitieron: {lista}')
                if nuevas_cat:
                    messages.warning(request, f'🆕 Categorías nuevas creadas: {", ".join(nuevas_cat)}. Revisa que estén bien escritas.')
                if errores:
                    lista = ' | '.join(errores[:10]) + (' ...' if len(errores) > 10 else '')
                    messages.error(request, f'⚠️ {len(errores)} filas con error: {lista}')
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

