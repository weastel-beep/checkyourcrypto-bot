"""
Автоматическое определение блокчейна по формату адреса
"""
import re
from typing import Optional


def detect_chain(address: str) -> Optional[str]:
    """
    Автоматически определяет блокчейн по формату адреса
    
    Args:
        address: Криптоадрес для анализа
        
    Returns:
        Строка с названием блокчейна или None если не удалось определить
    """
    # Проверяем на None и пустые значения
    if not address:
        return None
    
    # Убираем пробелы
    address = address.strip()
    
    # Проверяем на пустую строку после strip
    if not address:
        return None
    
    # Tron (начинается с T, 34 символа) - проверяем ПЕРЕД приведением к нижнему регистру!
    if re.match(r'^T[a-km-zA-HJ-NP-Z1-9]{33}$', address) and len(address) == 34:
        return 'tron'
    
    # Приводим к нижнему регистру для остальных проверок
    address_lower = address.lower()
    
    # Bitcoin (начинается с 1, 3, bc1)
    if re.match(r'^(1|3)[a-km-zA-HJ-NP-Z1-9]{25,34}$', address) or address_lower.startswith('bc1'):
        return 'btc'
    
    # Solana (начинается с различными символами, 32-44 символа)
    if re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address_lower) and not address_lower.startswith('0x'):
        return 'solana'
    
    # Ethereum и EVM-совместимые (начинается с 0x, 42 символов)
    # По умолчанию считаем Ethereum, так как это самый популярный
    if re.match(r'^0x[a-fA-F0-9]{40}$', address_lower):
        return 'eth'
    
    # Если не удалось определить, возвращаем None
    return None


def is_valid_crypto_address(address: str) -> bool:
    """
    Проверяет, является ли строка валидным криптоадресом
    
    Args:
        address: Строка для проверки
        
    Returns:
        True если это валидный криптоадрес, False иначе
    """
    return detect_chain(address) is not None
