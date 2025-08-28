"""add_menu_management_tables

Revision ID: add_menu_management_tables
Revises: 9701551ba0c4
Create Date: 2025-08-23 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_menu_management_tables'
down_revision = '9701551ba0c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу для меню
    op.create_table('bot_menus',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),  # main_menu, settings_menu, etc.
        sa.Column('language', sa.String(length=10), nullable=False),  # ru, en, etc.
        sa.Column('menu_type', sa.String(length=50), nullable=False),  # reply_keyboard, inline_keyboard
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'language', name='uq_menu_name_language')
    )
    
    # Создаем таблицу для элементов меню
    op.create_table('bot_menu_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('menu_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=200), nullable=False),  # Текст кнопки
        sa.Column('callback_data', sa.String(length=200), nullable=True),  # callback_data для inline кнопок
        sa.Column('row_position', sa.Integer(), nullable=False, default=0),  # Позиция в ряду
        sa.Column('column_position', sa.Integer(), nullable=False, default=0),  # Позиция в колонке
        sa.Column('parent_item_id', sa.Integer(), nullable=True),  # Для подменю
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['menu_id'], ['bot_menus.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_item_id'], ['bot_menu_items.id'], ondelete='CASCADE')
    )
    
    # Создаем таблицу для связки меню с текстами
    op.create_table('menu_text_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('text_category', sa.String(length=100), nullable=False),  # welcome, main_menu, etc.
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['menu_item_id'], ['bot_menu_items.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('menu_item_id', 'text_category', 'language', name='uq_menu_text_link')
    )


def downgrade() -> None:
    op.drop_table('menu_text_links')
    op.drop_table('bot_menu_items')
    op.drop_table('bot_menus')
