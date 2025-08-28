"""
URL configuration for core app
"""
from django.urls import path
from . import views, admin_views, text_api

app_name = 'core'

urlpatterns = [
    # API endpoints
    path('stats/', views.stats, name='stats'),
    path('health/', views.health, name='health'),
    path('text/get/', views.api_get_text, name='api_get_text'),
    path('text/set/', views.api_set_text, name='api_set_text'),
    path('setting/get/', views.api_get_setting, name='api_get_setting'),
    path('setting/set/', views.api_set_setting, name='api_set_setting'),
    path('outbox/create/', views.api_create_outbox, name='api_create_outbox'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Тестовый URL для диагностики
    path('test/', admin_views.test_view, name='test_view'),
    path('test-texts/', admin_views.test_texts_page, name='test_texts_page'),
    
    # Admin panel URLs (custom admin)
    path('panel/login/', admin_views.admin_login, name='admin_login'),
    path('panel/logout/', admin_views.admin_logout, name='admin_logout'),
    path('panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('panel/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),

    

    
    # API для текстов бота
    path('panel/texts/category/', text_api.get_texts_by_category, name='get_texts_by_category'),
    path('panel/texts/save/', text_api.save_text, name='save_text'),
    path('panel/texts/save-all/', text_api.save_all_texts, name='save_all_texts'),
    path('panel/texts/import/', text_api.import_texts, name='import_texts'),
    path('panel/texts/sync-to-bot/', text_api.sync_texts_to_bot, name='sync_texts_to_bot'),
    path('panel/texts/languages/', text_api.get_languages, name='get_languages'),
    path('panel/texts/categories/', text_api.get_categories, name='get_categories'),
    
    path('panel/users/', admin_views.admin_users, name='admin_users'),
    path('panel/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('panel/users/<int:user_id>/block/', admin_views.admin_user_block, name='admin_user_block'),
    path('panel/users/<int:user_id>/unblock/', admin_views.admin_user_unblock, name='admin_user_unblock'),
    path('panel/users/<int:user_id>/balance/', admin_views.api_change_user_balance, name='api_change_user_balance'),
    path('panel/messages/', admin_views.admin_messages, name='admin_messages'),
    path('panel/messages/create/', admin_views.admin_create_message, name='admin_create_message'),
    path('panel/messages/<int:message_id>/send/', admin_views.admin_send_message, name='admin_send_message'),
    path('panel/messages/<int:message_id>/start-mass-send/', admin_views.admin_start_mass_send, name='admin_start_mass_send'),
    path('panel/messages/<int:message_id>/get/', admin_views.admin_get_message, name='admin_get_message'),
    path('panel/messages/<int:message_id>/edit/', admin_views.admin_edit_message, name='admin_edit_message'),
    path('panel/messages/<int:message_id>/delete/', admin_views.admin_delete_message, name='admin_delete_message'),
    
    # Управление массовой рассылкой
    path('panel/mass-send/sessions/', admin_views.admin_mass_send_sessions, name='admin_mass_send_sessions'),
    path('panel/mass-send/sessions/<int:session_id>/status/', admin_views.admin_mass_send_status, name='admin_mass_send_status'),
    path('panel/mass-send/sessions/<int:session_id>/control/', admin_views.admin_mass_send_control, name='admin_mass_send_control'),
    path('panel/mass-send/sessions/<int:session_id>/details/', admin_views.admin_mass_send_details, name='admin_mass_send_details'),
    path('panel/texts/', admin_views.admin_texts, name='admin_texts'),
    path('panel/texts/category/', admin_views.admin_text_category, name='admin_text_category'),
    
    # Admin API endpoints
    path('api/dashboard/stats/', admin_views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/users/', admin_views.api_users_list, name='api_users_list'),
    path('api/users/<int:user_id>/action/', admin_views.api_user_action, name='api_user_action'),
    path('panel/users/<int:user_id>/balance/', admin_views.api_change_user_balance, name='api_change_user_balance'),
    path('panel/users/<int:user_id>/block/', admin_views.api_block_user, name='api_block_user'),
    path('panel/users/<int:user_id>/unblock/', admin_views.api_unblock_user, name='api_unblock_user'),
    path('panel/users/<int:user_id>/message/', admin_views.api_send_user_message, name='api_send_user_message'),
    path('panel/users/<int:user_id>/test/', admin_views.test_message_api, name='test_message_api'),
]
