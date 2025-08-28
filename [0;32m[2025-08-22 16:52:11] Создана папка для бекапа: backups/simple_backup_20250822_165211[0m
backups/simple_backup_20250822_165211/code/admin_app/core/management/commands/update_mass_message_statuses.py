from django.core.management.base import BaseCommand
from core.admin_models import MassMessage

class Command(BaseCommand):
    help = 'Обновляет статусы массовых сообщений с строчных на заглавные'

    def handle(self, *args, **options):
        # Маппинг старых значений на новые
        status_mapping = {
            'draft': 'DRAFT',
            'scheduled': 'SCHEDULED', 
            'sending': 'SENDING',
            'completed': 'COMPLETED',
            'cancelled': 'CANCELLED',
            'failed': 'FAILED'
        }
        
        # Получаем все массовые сообщения
        messages = MassMessage.objects.all()
        updated_count = 0
        
        self.stdout.write(f"Найдено {messages.count()} массовых сообщений")
        
        for message in messages:
            old_status = message.status
            new_status = status_mapping.get(old_status)
            
            if new_status and old_status != new_status:
                self.stdout.write(f"Обновляем сообщение {message.id}: {old_status} -> {new_status}")
                message.status = new_status
                message.save()
                updated_count += 1
            elif old_status in status_mapping:
                self.stdout.write(f"Сообщение {message.id}: статус уже правильный ({old_status})")
            else:
                self.stdout.write(f"Сообщение {message.id}: неизвестный статус ({old_status})")
        
        self.stdout.write(self.style.SUCCESS(f"\nОбновлено {updated_count} сообщений"))
