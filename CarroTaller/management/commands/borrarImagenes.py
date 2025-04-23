from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Exists
from datetime import timedelta
from CarroTaller.models import EvidenciaRegistro
import os

class Command(BaseCommand):
    help = 'Borra fotos antiguas (más de 7 días) siempre que haya fotos más recientes en el sistema.'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        fecha_corte = hoy - timedelta(days=7)

        # Consulta para saber si hay cualquier evidencia posterior a la fecha de corte
        evidencias_nuevas = EvidenciaRegistro.objects.filter(
            fecha__gt=fecha_corte
        ).values('pk')

        # Selecciona fotos con fecha <= fecha_corte y que existan evidencias nuevas
        candidatas = EvidenciaRegistro.objects.annotate(
            tiene_nuevas=Exists(evidencias_nuevas)
        ).filter(
            fecha__lte=fecha_corte,
            tiene_nuevas=True
        )

        total = candidatas.count()
        self.stdout.write(f'→ {total} fotos antiguas candidatas a borrarse.')

        for ev in candidatas:
            ruta_archivo = ev.ruta.path
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)
                self.stdout.write(f'   • Se borró foto {ev.pk}: {ruta_archivo}')
            ev.delete()

        self.stdout.write(self.style.SUCCESS('Limpieza de evidencias completada.'))