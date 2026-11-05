from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType


def registrar(request, obj, mensaje, accion=CHANGE):
    """Guarda un movimiento en el historial con el usuario que lo hizo."""
    if not request.user.is_authenticated:
        return
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=accion,
        change_message=mensaje,
    )


def registrar_exportacion(request, queryset, nombre):
    """Guarda en el historial que alguien exportó a Excel."""
    if not request.user.is_authenticated:
        return
    LogEntry.objects.create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(queryset.model),
        object_repr=f'Exportación {nombre}',
        action_flag=CHANGE,
        change_message=f'📥 Exportó {queryset.count()} registro(s) a Excel',
    )