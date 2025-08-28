"""
Django models for admin app
"""
from django.db import models
from decimal import Decimal

# Импортируем модели админки
from .admin_models import AdminUser, AdminInvitation, AdminActionLog, SystemMetrics, MassMessage, BotText


class User(models.Model):
    """Пользователь бота"""
    tg_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=10, default='ru')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_blocked = models.BooleanField(default=False)
    last_free_check = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    referrer_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"User {self.tg_id}"


class Check(models.Model):
    """Проверка адреса"""
    CHECK_TYPES = [
        ('free', 'Бесплатная'),
        ('paid', 'Платная'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    address = models.CharField(max_length=255)
    chain = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=CHECK_TYPES)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'checks'
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'

    def __str__(self):
        return f"Check {self.id} - {self.address[:10]}..."


class Payment(models.Model):
    """Платеж"""
    PAYMENT_STATUSES = [
        ('pending', 'Ожидает'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
    ]
    
    PAYMENT_METHODS = [
        ('binance', 'Binance Pay'),
        ('crypto', 'Crypto'),
        ('card', 'Card'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    tx_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"


class Setting(models.Model):
    """Настройки системы"""
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return f"Setting {self.key}"


class Text(models.Model):
    """Тексты для бота"""
    lang = models.CharField(max_length=10)
    key = models.CharField(max_length=100)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'texts'
        unique_together = ['lang', 'key']
        verbose_name = 'Текст'
        verbose_name_plural = 'Тексты'

    def __str__(self):
        return f"Text {self.lang}:{self.key}"


class PaymentMethod(models.Model):
    """Методы оплаты"""
    name = models.CharField(max_length=50, primary_key=True)
    enabled = models.BooleanField(default=True)
    logo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Метод оплаты'
        verbose_name_plural = 'Методы оплаты'

    def __str__(self):
        return f"Payment Method {self.name}"


class Referral(models.Model):
    """Рефералы"""
    REWARD_TYPES = [
        ('balance', 'Баланс'),
        ('free_check', 'Бесплатная проверка'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    invited_id = models.BigIntegerField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'referrals'
        verbose_name = 'Реферал'
        verbose_name_plural = 'Рефералы'

    def __str__(self):
        return f"Referral {self.id}"


class Outbox(models.Model):
    """Исходящие сообщения"""
    OUTBOX_STATUSES = [
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=OUTBOX_STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'outbox'
        verbose_name = 'Исходящее сообщение'
        verbose_name_plural = 'Исходящие сообщения'

    def __str__(self):
        return f"Outbox {self.id}"
