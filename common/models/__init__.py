"""
Модуль моделей данных
"""

# Импортируем все из основного файла models.py
from .. import models

# Импортируем новые единые модели
from .unified import UnifiedBotText, UnifiedScenario, UnifiedSetting

# Экспортируем все модели
__all__ = [
    # Все модели из основного файла
    *[attr for attr in dir(models) if not attr.startswith('_')],
    # Новые единые модели
    "UnifiedBotText",
    "UnifiedScenario", 
    "UnifiedSetting"
]
