# Generated manually for admin models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('role', models.CharField(choices=[('superadmin', 'Superadmin'), ('admin', 'Admin'), ('moderator', 'Moderator')], default='moderator', max_length=20)),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('two_factor_enabled', models.BooleanField(default=False)),
                ('two_factor_secret', models.CharField(blank=True, max_length=32)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='adminuser_set', related_query_name='adminuser', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='adminuser_set', related_query_name='adminuser', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Администратор',
                'verbose_name_plural': 'Администраторы',
                'db_table': 'admin_users',
            },
        ),
        migrations.CreateModel(
            name='AdminInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(choices=[('superadmin', 'Superadmin'), ('admin', 'Admin'), ('moderator', 'Moderator')], default='moderator', max_length=20)),
                ('token', models.CharField(max_length=64, unique=True)),
                ('is_used', models.BooleanField(default=False)),
                ('expires_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to='core.adminuser')),
            ],
            options={
                'verbose_name': 'Приглашение',
                'verbose_name_plural': 'Приглашения',
                'db_table': 'admin_invitations',
            },
        ),
        migrations.CreateModel(
            name='AdminActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('user_block', 'Блокировка пользователя'), ('user_unblock', 'Разблокировка пользователя'), ('balance_change', 'Изменение баланса'), ('message_send', 'Отправка сообщения'), ('text_edit', 'Редактирование текста'), ('admin_create', 'Создание администратора'), ('admin_delete', 'Удаление администратора'), ('system_restart', 'Перезапуск системы')], max_length=20)),
                ('description', models.TextField()),
                ('target_user_id', models.BigIntegerField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='core.adminuser')),
            ],
            options={
                'verbose_name': 'Лог действия',
                'verbose_name_plural': 'Логи действий',
                'db_table': 'admin_action_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SystemMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_usage', models.FloatField()),
                ('memory_usage', models.FloatField()),
                ('active_users', models.IntegerField()),
                ('requests_per_minute', models.IntegerField()),
                ('bot_status', models.CharField(max_length=20)),
                ('database_connections', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Метрика системы',
                'verbose_name_plural': 'Метрики системы',
                'db_table': 'system_metrics',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='MassMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('language', models.CharField(default='ru', max_length=10)),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('scheduled', 'Запланировано'), ('sending', 'Отправляется'), ('completed', 'Завершено'), ('cancelled', 'Отменено'), ('failed', 'Ошибка')], default='draft', max_length=20)),
                ('min_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('max_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('user_language', models.CharField(blank=True, max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('total_users', models.IntegerField(default=0)),
                ('sent_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_messages', to='core.adminuser')),
            ],
            options={
                'verbose_name': 'Массовое сообщение',
                'verbose_name_plural': 'Массовые сообщения',
                'db_table': 'mass_messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BotText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_type', models.CharField(choices=[('welcome', 'Приветствие'), ('check_instructions', 'Инструкции проверки'), ('check_result', 'Результат проверки'), ('payment_info', 'Информация о платежах'), ('profile_info', 'Информация профиля'), ('faq', 'FAQ'), ('error_message', 'Сообщения об ошибках')], max_length=50)),
                ('language', models.CharField(max_length=10)),
                ('content', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_texts', to='core.adminuser')),
            ],
            options={
                'verbose_name': 'Текст бота',
                'verbose_name_plural': 'Тексты бота',
                'db_table': 'bot_texts',
                'ordering': ['text_type', 'language', '-version'],
                'unique_together': {('text_type', 'language', 'version')},
            },
        ),
    ]
