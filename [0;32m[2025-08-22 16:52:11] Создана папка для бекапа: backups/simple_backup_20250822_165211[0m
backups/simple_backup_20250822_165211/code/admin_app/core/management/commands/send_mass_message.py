"""
Django management command для отправки массовых сообщений
"""
import asyncio
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from aiogram import Bot

from core.simple_mass_messaging import init_mass_messaging_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправить массовое сообщение'

    def add_arguments(self, parser):
        parser.add_argument('message_id', type=int, help='ID массового сообщения')
        parser.add_argument(
            '--prepare-only',
            action='store_true',
            help='Только подготовить сообщение, не отправлять'
        )

    def handle(self, *args, **options):
        message_id = options['message_id']
        prepare_only = options['prepare_only']

        try:
            # Создаем бота и сервис
            bot = Bot(token=settings.BOT_TOKEN)
            service = init_mass_messaging_service(bot)

            if prepare_only:
                # Только подготовка
                result = service.prepare_mass_message(message_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Сообщение {message_id} подготовлено: {result["total_users"]} получателей'
                    )
                )
            else:
                # Отправка
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(service.send_mass_message(message_id))
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Сообщение {message_id} отправлено: {result["success"]} успешно, {result["failed"]} ошибок'
                        )
                    )
                finally:
                    loop.close()

        except Exception as e:
            raise CommandError(f'Ошибка отправки сообщения {message_id}: {e}')
