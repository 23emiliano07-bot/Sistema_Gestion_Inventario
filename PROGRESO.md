# PROGRESO — Sistema de Gestión de Inventario (BAMASA)

> Actualiza este archivo al terminar cada sesión de trabajo.
> Al abrir un chat nuevo con Claude, pega este archivo para retomar donde te quedaste.

---

## Datos del proyecto

- **Framework:** Django 4.2 + Django REST Framework 3.14
- **Ruta local:** `C:\Users\Emiliano\Sistema_Gestion_Inventario\`
- **GitHub:** cuenta `23emiliano07-bot`
- **Producción:** emilianomontoya.pythonanywhere.com (SQLite, máx. 2 usuarios)
- **Docker:** imagen `sistemainventario26`, contenedor `inventario26`, puerto 8000
- **Cursos:** Aplicaciones Web 2 (proyecto) y Aplicaciones Web 1 (Docker)

## Apps

- `productos` — catálogo con imágenes (se espera ~5,000 productos)
- `proveedores` — CRUD completo
- `pedidos` — máquina de estados + detalles + BackOrders
- `almacenes` — CRUD (Almacén Central, Sandra, otros)
- `usuarios` — grupos y permisos

---

## ✅ Ya terminado

### Base
- [x] CRUD completo en todas las apps (modelos, DAOs, serializers, viewsets, forms, views, urls, templates)
- [x] Validaciones de datos (`validar_precio_positivo`, métodos `clean()`)
- [x] Campos de imagen (`ImageField`) y configuración de media
- [x] Middleware de auditoría
- [x] Admin personalizado
- [x] Página de inicio con banner y navbar (Almacenes, Back Orders)
- [x] Docker funcionando
- [x] Desplegado en PythonAnywhere
- [x] `requirements.txt` en GitHub

### Pedidos — máquina de estados
- [x] Flujo: **Pendiente → Confirmado → Solicitado → Entregado** (Eliminar desde cualquier estado, no hay "Cancelado")
- [x] Al crear un pedido solo se permite el estado Pendiente
- [x] No se puede regresar a un estado anterior
- [x] Orden de compra / Orden de venta: editables solo en Confirmado
- [x] Responsable: se llena solo con el usuario logueado en Solicitado
- [x] Tabla dinámica: columnas 1-5 (No, Producto, Almacén, Cantidad, Total a pedir); columnas 6-8 (Recibido, Pendiente, Folio factura) solo en Entregado
- [x] Botón (+) para agregar varios almacenes por producto; Total a pedir se suma solo
- [x] No se permiten productos duplicados por almacén en el mismo pedido (`unique_together` + `clean()`)
- [x] Se quitó `fecha_entrega`; `fecha_pedido` usa `auto_now=True`
- [x] Todos los usuarios pueden cambiar estados

### BackOrders
- [x] Se crea solo cuando Pendiente > 0 al guardar en Entregado
- [x] Se borra / se marca resuelto cuando Pendiente = 0
- [x] Filtro por proveedor en el admin

### Búsqueda de productos
- [x] Autocomplete personalizado: se intentó y se revirtió (muy complejo)
- [x] Se usa `raw_id_fields` en el admin para buscar productos

### Permisos (fase actual)
- [x] Grupos creados a mano en el Admin: Jefatura, Gerencia, Coordinación, Empleados
- [x] Un usuario de prueba por grupo (todos con `is_staff = True`)
- [x] Archivo `permission_decorators.py` generado (`@group_required`, `@permission_required_custom`, `GroupRequiredMixin`)

---

## 🔄 Pendiente (siguiente paso)

- [ ] Presentar permisos al profesor para validación
- [ ] Proteger las vistas con los decoradores / mixins
- [ ] Mostrar u ocultar botones según el grupo del usuario

## 💡 Ideas / después

- [ ] Que la app funcione bien en celular (uso en campo)

---

## ⚠️ Errores que se repiten

- Migraciones fallan si las URLs de la app están activas → comentarlas, migrar, descomentar
- Importaciones circulares en los DAOs
- Rutas de templates mal escritas en las vistas
- Usuarios de prueba sin `is_staff = True` no entran al Admin

---

## 📝 Bitácora

| Fecha | Qué hice | Qué sigue |
|-------|----------|-----------|
| 2026-08-30 | Docker terminado | — |
| 2026-09-02 | Máquina de estados y Almacenes | BackOrders |
| 2026-09-04 | Deploy en PythonAnywhere | — |
| 2026-09-05 | BackOrders terminados | Búsqueda de productos |
| 2026-09-08 | `raw_id_fields` para productos | Permisos |
| 2026-09-28 | Grupos y usuarios de prueba | Proteger vistas |
| 2026-10-21 | Creé este archivo | Revisar qué avancé después del 28/09 |
