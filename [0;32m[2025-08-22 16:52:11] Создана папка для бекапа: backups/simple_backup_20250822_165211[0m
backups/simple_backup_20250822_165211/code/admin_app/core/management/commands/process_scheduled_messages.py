"""
Django management command для обработки запланированных сообщений
"""
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot

from core.simple_mass_messaging import init_mass_messaging_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Обработать запланированные массовые сообщения'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            action='store_true',
            help='Работать в бесконечном цикле'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Интервал проверки в секундах (по умолчанию 60)'
        )

    def handle(self, *args, **options):
        loop_mode = options['loop']
        interval = options['interval']
        try:
            # Создаем бота и сервис
            bot = Bot(token=settings.BOT_TOKEN)
            service = init_mass_messaging_service(bot)

            if loop_mode:
                # Работа в бесконечном цикле
                import time
                self.stdout.write(
                    self.style.SUCCESS(f'Запуск воркера запланированных сообщений (интервал: {interval}с)')
                )
                
                while True:
                    try:
                        # Обрабатываем запланированные сообщения
                        result = service.process_scheduled_messages()
                        
                        if result["processed"] > 0:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Обработано сообщений: {result["processed"]}, '
                                    f'успешно: {result["success"]}, '
                                    f'ошибок: {result["failed"]}'
                                )
                            )
                        
                        # Ждем следующей проверки
                        time.sleep(interval)
                        
                    except KeyboardInterrupt:
                        self.stdout.write(self.style.WARNING('Воркер остановлен'))
                        break
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Ошибка в цикле: {e}')
                        )
                        time.sleep(interval)
            else:
                # Одноразовая обработка
                result = service.process_scheduled_messages()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Обработано сообщений: {result["processed"]}, '
                        f'успешно: {result["success"]}, '
                        f'ошибок: {result["failed"]}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка обработки запланированных сообщений: {e}')
            )
