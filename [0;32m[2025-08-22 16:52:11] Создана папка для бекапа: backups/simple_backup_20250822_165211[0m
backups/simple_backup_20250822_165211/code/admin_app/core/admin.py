"""
Django admin interface
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, Check, Payment, Setting, Text, PaymentMethod, Referral, Outbox


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'language', 'balance', 'checks_count', 'last_free_check', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['tg_id', 'referral_code']
    readonly_fields = ['created_at', 'updated_at']
    
    def checks_count(self, obj):
        return obj.check_set.count()
    checks_count.short_description = 'Проверок'


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'address_short', 'chain', 'type', 'created_at']
    list_filter = ['type', 'chain', 'created_at']
    search_fields = ['address', 'user__tg_id']
    readonly_fields = ['created_at', 'result_preview']
    
    def user_link(self, obj):
        url = reverse('admin:core_user_change', args=[obj.user.tg_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.tg_id)
    user_link.short_description = 'Пользователь'
    
    def address_short(self, obj):
        return f"{obj.address[:10]}..." if len(obj.address) > 10 else obj.address
    address_short.short_description = 'Адрес'
    
    def result_preview(self, obj):
        if obj.result:
            return format_html('<pre>{}</pre>', str(obj.result)[:500])
        return '-'
    result_preview.short_description = 'Результат'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['user__tg_id', 'tx_id']
    readonly_fields = ['created_at']
    
    def user_link(self, obj):
        url = reverse('admin:core_user_change', args=[obj.user.tg_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.tg_id)
    user_link.short_description = 'Пользователь'


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_short', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
    
    def value_short(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_short.short_description = 'Значение'


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['lang', 'key', 'value_short', 'updated_at']
    list_filter = ['lang', 'updated_at']
    search_fields = ['key', 'value']
    readonly_fields = ['updated_at']
    
    def value_short(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_short.short_description = 'Текст'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'logo_preview', 'created_at']
    list_filter = ['enabled', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'logo_preview']
    
    def logo_preview(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo_url)
        return '-'
    logo_preview.short_description = 'Логотип'


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'invited_id', 'reward_type', 'reward_amount', 'created_at']
    list_filter = ['reward_type', 'created_at']
    search_fields = ['user__tg_id', 'invited_id']
    readonly_fields = ['created_at']
    
    def user_link(self, obj):
        url = reverse('admin:core_user_change', args=[obj.user.tg_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.tg_id)
    user_link.short_description = 'Пользователь'


@admin.register(Outbox)
class OutboxAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__tg_id']
    readonly_fields = ['created_at', 'sent_at', 'payload_preview']
    
    def user_link(self, obj):
        url = reverse('admin:core_user_change', args=[obj.user.tg_id])
        return format_html('<a href="{}">{}</a>', url, obj.user.tg_id)
    user_link.short_description = 'Пользователь'
    
    def payload_preview(self, obj):
        if obj.payload:
            return format_html('<pre>{}</pre>', str(obj.payload)[:500])
        return '-'
    payload_preview.short_description = 'Данные'


# Настройка админки
admin.site.site_header = "Check Your Crypto - Админка"
admin.site.site_title = "Check Your Crypto"
admin.site.index_title = "Панель управления"
