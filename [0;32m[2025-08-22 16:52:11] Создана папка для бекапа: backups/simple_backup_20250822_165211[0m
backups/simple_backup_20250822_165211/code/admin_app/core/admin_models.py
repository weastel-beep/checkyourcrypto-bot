"""
Модели для админки Check Your Crypto
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import secrets
import string

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class AdminRole(str, Enum):
    """Роли администраторов"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AdminUser(AbstractUser):
    """Модель администратора"""
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.value.title()) for role in AdminRole],
        default=AdminRole.MODERATOR.value
    )
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_users"
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    def __str__(self):
        return f"{self.username} ({self.role})"

    def can_manage_users(self) -> bool:
        """Может ли управлять пользователями"""
        return self.role in [AdminRole.SUPERADMIN.value, AdminRole.ADMIN.value]

    def can_manage_admins(self) -> bool:
        """Может ли управлять администраторами"""
        return self.role == AdminRole.SUPERADMIN.value

    def can_send_messages(self) -> bool:
        """Может ли отправлять массовые сообщения"""
        return self.role in [AdminRole.SUPERADMIN.value, AdminRole.ADMIN.value]

    def can_manage_texts(self) -> bool:
        """Может ли управлять текстами"""
        return self.role in [AdminRole.SUPERADMIN.value, AdminRole.ADMIN.value]


class AdminInvitation(models.Model):
    """Приглашения для доступа к админке"""
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.value.title()) for role in AdminRole],
        default=AdminRole.MODERATOR.value
    )
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(
        AdminUser, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations'
    )
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_invitations"
        verbose_name = "Приглашение"
        verbose_name_plural = "Приглашения"

    def __str__(self):
        return f"Приглашение для {self.email} ({self.role})"

    def is_expired(self) -> bool:
        """Проверяет, истекло ли приглашение"""
        return timezone.now() > self.expires_at

    @classmethod
    def generate_token(cls) -> str:
        """Генерирует уникальный токен"""
        return secrets.token_urlsafe(32)

    @classmethod
    def create_invitation(cls, email: str, role: str, invited_by: AdminUser) -> 'AdminInvitation':
        """Создает новое приглашение"""
        return cls.objects.create(
            email=email,
            role=role,
            token=cls.generate_token(),
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7)  # 7 дней на активацию
        )


class AdminActionLog(models.Model):
    """Лог действий администраторов"""
    ACTION_TYPES = [
        ('admin_login', 'Вход администратора'),
        ('admin_logout', 'Выход администратора'),
        ('user_block', 'Блокировка пользователя'),
        ('user_unblock', 'Разблокировка пользователя'),
        ('balance_change', 'Изменение баланса'),
        ('personal_message_send', 'Отправка персонального сообщения'),
        ('mass_message_send', 'Отправка массового сообщения'),
        ('text_edit', 'Редактирование текста'),
        ('admin_create', 'Создание администратора'),
        ('admin_delete', 'Удаление администратора'),
        ('system_restart', 'Перезапуск системы'),
        ('user_view', 'Просмотр профиля пользователя'),
        ('user_activity_view', 'Просмотр активности пользователя'),
    ]

    admin = models.ForeignKey(
        AdminUser, 
        on_delete=models.CASCADE, 
        related_name='action_logs'
    )
    action_type = models.CharField(max_length=25, choices=ACTION_TYPES)
    description = models.TextField()
    target_user_id = models.BigIntegerField(null=True, blank=True)  # ID пользователя бота
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_action_logs"
        verbose_name = "Лог действия"
        verbose_name_plural = "Логи действий"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin.username} - {self.get_action_type_display()} - {self.created_at}"


class SystemMetrics(models.Model):
    """Метрики системы"""
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()  # Процент использования CPU
    memory_usage = models.FloatField()  # Процент использования памяти
    active_users = models.IntegerField()  # Количество активных пользователей
    requests_per_minute = models.IntegerField()  # Запросов в минуту
    bot_status = models.CharField(max_length=20)  # online/offline/error
    database_connections = models.IntegerField()  # Количество подключений к БД

    class Meta:
        db_table = "system_metrics"
        verbose_name = "Метрика системы"
        verbose_name_plural = "Метрики системы"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Метрики на {self.timestamp}"


class MassMessage(models.Model):
    """Массовые сообщения"""
    STATUS_CHOICES = [
        ('DRAFT', 'Черновик'),
        ('SCHEDULED', 'Запланировано'),
        ('SENDING', 'Отправляется'),
        ('COMPLETED', 'Завершено'),
        ('CANCELLED', 'Отменено'),
        ('FAILED', 'Ошибка'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    language = models.CharField(max_length=10, default='ru')  # ru/en
    created_by = models.ForeignKey(
        AdminUser, 
        on_delete=models.CASCADE, 
        related_name='created_messages',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Фильтры для выборки пользователей
    user_filter = models.CharField(max_length=20, default='all', blank=True)  # all/active/new/balance/language
    min_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user_language = models.CharField(max_length=10, blank=True)  # ru/en
    is_active_only = models.BooleanField(default=True, db_column='is_active')  # только активные пользователи
    
    # Планирование
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Статистика
    total_users = models.IntegerField(default=0)  # Общее количество пользователей
    sent_count = models.IntegerField(default=0)  # Отправлено
    failed_count = models.IntegerField(default=0)  # Ошибок
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mass_messages"
        verbose_name = "Массовое сообщение"
        verbose_name_plural = "Массовые сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def is_scheduled(self) -> bool:
        """Проверяет, запланировано ли сообщение"""
        return self.status == 'SCHEDULED' and self.scheduled_at

    def can_be_sent(self) -> bool:
        """Проверяет, можно ли отправить сообщение"""
        return self.status in ['DRAFT', 'SCHEDULED'] and not self.sent_at


class BotText(models.Model):
    """Тексты бота для разных языков"""
    CATEGORIES = [
        ('welcome', 'Приветственные сообщения'),
        ('main_menu', 'Главное меню'),
        ('check', 'Сообщения проверки'),
        ('check_choice', 'Выбор типа проверки'),
        ('check_result', 'Результат проверки'),
        ('payment', 'Платежные сообщения'),
        ('error', 'Сообщения об ошибках'),
        ('help', 'Справка и помощь'),
        ('settings', 'Настройки'),
        ('insufficient_balance', 'Недостаточно средств'),
        ('user_blocked', 'Пользователь заблокирован'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORIES, default='welcome')
    language = models.CharField(max_length=10)  # ru/en/es/fr/de/etc
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    created_by = models.ForeignKey(
        AdminUser, 
        on_delete=models.CASCADE, 
        related_name='created_texts',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bot_texts"
        verbose_name = "Текст бота"
        verbose_name_plural = "Тексты бота"
        unique_together = ['category', 'language', 'version']
        ordering = ['category', 'language', '-version']

    def __str__(self):
        return f"{self.get_category_display()} ({self.language}) v{self.version}"

    @classmethod
    def get_active_text(cls, category: str, language: str) -> Optional['BotText']:
        """Получает активный текст для указанной категории и языка"""
        return cls.objects.filter(
            category=category,
            language=language,
            is_active=True
        ).order_by('-version').first()


class UserMessage(models.Model):
    """Персональные сообщения пользователям"""
    MESSAGE_TYPES = [
        ('personal', 'Персональное сообщение'),
        ('mass', 'Массовая рассылка'),
        ('system', 'Системное сообщение'),
        ('support', 'Поддержка'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает отправки'),
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('read', 'Прочитано'),
        ('failed', 'Ошибка отправки'),
    ]

    user_id = models.BigIntegerField()  # ID пользователя бота
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='personal')
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    language = models.CharField(max_length=10, default='ru')  # ru/en
    
    # Отправитель
    sent_by = models.ForeignKey(
        AdminUser, 
        on_delete=models.CASCADE, 
        related_name='sent_user_messages'
    )
    
    # Статус и метаданные
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Связь с массовым сообщением (если это часть массовой рассылки)
    mass_message = models.ForeignKey(
        MassMessage, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='user_messages'
    )
    
    # Ошибки
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_messages"
        verbose_name = "Сообщение пользователю"
        verbose_name_plural = "Сообщения пользователям"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['message_type', 'created_at']),
        ]

    def __str__(self):
        return f"Сообщение {self.user_id} от {self.sent_by.username} ({self.get_status_display()})"

    def mark_as_sent(self):
        """Отмечает сообщение как отправленное"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()

    def mark_as_delivered(self):
        """Отмечает сообщение как доставленное"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()

    def mark_as_read(self):
        """Отмечает сообщение как прочитанное"""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()

    def mark_as_failed(self, error_message: str):
        """Отмечает сообщение как неудачное"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


class MassSendSession(models.Model):
    """Сессия массовой рассылки"""
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает'),
        ('RUNNING', 'Выполняется'),
        ('PAUSED', 'Приостановлено'),
        ('COMPLETED', 'Завершено'),
        ('FAILED', 'Ошибка'),
        ('CANCELLED', 'Отменено'),
    ]

    message = models.ForeignKey(MassMessage, on_delete=models.CASCADE, related_name='send_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Прогресс
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)  # Уже отправлено ранее
    
    # Временные метки
    started_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Настройки отправки
    batch_size = models.IntegerField(default=50)  # Размер пакета
    delay_between_batches = models.IntegerField(default=1)  # Задержка между пакетами (секунды)
    delay_between_messages = models.FloatField(default=0.1)  # Задержка между сообщениями (секунды)
    
    # Обработка ошибок
    max_retries = models.IntegerField(default=3)
    current_retry = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Контроль
    is_cancelled = models.BooleanField(default=False)
    created_by = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name='send_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mass_send_sessions"
        verbose_name = "Сессия рассылки"
        verbose_name_plural = "Сессии рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сессия {self.id} - {self.message.title} ({self.get_status_display()})"

    @property
    def progress_percentage(self):
        """Процент выполнения"""
        if self.total_recipients == 0:
            return 0
        return round((self.sent_count + self.failed_count + self.skipped_count) / self.total_recipients * 100, 1)

    @property
    def remaining_count(self):
        """Оставшееся количество"""
        return self.total_recipients - (self.sent_count + self.failed_count + self.skipped_count)

    @property
    def is_active(self):
        """Активна ли сессия"""
        return self.status in ['PENDING', 'RUNNING']

    def can_resume(self):
        """Можно ли возобновить"""
        return self.status == 'PAUSED' and not self.is_cancelled

    def can_cancel(self):
        """Можно ли отменить"""
        return self.status in ['PENDING', 'RUNNING', 'PAUSED']

    def get_eta(self):
        """Оценка времени завершения"""
        if self.status not in ['RUNNING', 'PAUSED']:
            return None
        
        remaining = self.remaining_count
        if remaining == 0:
            return None
        
        # Расчет времени: сообщения + задержки между пакетами
        messages_time = remaining * self.delay_between_messages
        batches = remaining // self.batch_size + (1 if remaining % self.batch_size > 0 else 0)
        batch_delays = (batches - 1) * self.delay_between_batches
        
        total_seconds = messages_time + batch_delays
        
        from django.utils import timezone
        return timezone.now() + timezone.timedelta(seconds=total_seconds)


class MassSendRecipient(models.Model):
    """Получатель массовой рассылки"""
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает'),
        ('SENT', 'Отправлено'),
        ('FAILED', 'Ошибка'),
        ('SKIPPED', 'Пропущено'),
        ('BLOCKED', 'Заблокирован'),
    ]

    session = models.ForeignKey(MassSendSession, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='mass_send_recipients')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Детали отправки
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)  # ID сообщения в Telegram
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mass_send_recipients"
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        unique_together = ['session', 'user']  # Один пользователь - одна запись в сессии
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.tg_id} - {self.get_status_display()}"

    @property
    def can_retry(self):
        """Можно ли повторить отправку"""
        return self.status == 'FAILED' and self.retry_count < self.session.max_retries

    def mark_as_sent(self, telegram_message_id=None):
        """Отметить как отправленное"""
        from django.utils import timezone
        self.status = 'SENT'
        self.sent_at = timezone.now()
        if telegram_message_id:
            self.telegram_message_id = telegram_message_id
        self.save()

    def mark_as_failed(self, error_message):
        """Отметить как неудачное"""
        self.status = 'FAILED'
        self.retry_count += 1
        self.error_message = error_message
        self.save()

    def mark_as_skipped(self, reason="Уже отправлено ранее"):
        """Отметить как пропущенное"""
        self.status = 'SKIPPED'
        self.error_message = reason
        self.save()

    def mark_as_blocked(self):
        """Отметить как заблокированное"""
        self.status = 'BLOCKED'
        self.error_message = "Пользователь заблокирован"
        self.save()
