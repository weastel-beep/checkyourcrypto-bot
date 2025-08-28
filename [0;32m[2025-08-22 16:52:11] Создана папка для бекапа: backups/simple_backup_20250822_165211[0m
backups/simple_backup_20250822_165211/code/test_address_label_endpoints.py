#!/usr/bin/env python3
"""
Тест для поиска правильного эндпоинта Address Label API
"""
import asyncio
import logging
import sys
import os
import aiohttp

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_address_label_endpoints():
    """Тестирование различных эндпоинтов Address Label API"""
    logger.info("Тестируем различные эндпоинты Address Label API...")
    
    address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    chain = "eth"
    
    # Попробуем разные варианты эндпоинтов
    test_configs = [
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/address-label",
            "method": "GET",
            "params": {"address": address, "chain": chain}
        },
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/address-label",
            "method": "POST",
            "payload": {"address": address, "chain": chain}
        },
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/label",
            "method": "GET",
            "params": {"address": address, "chain": chain}
        },
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/label",
            "method": "POST",
            "payload": {"address": address, "chain": chain}
        },
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/address",
            "method": "GET",
            "params": {"address": address, "chain": chain}
        },
        {
            "url": "https://aml.blocksec.com/address-label/api/v3/address",
            "method": "POST",
            "payload": {"address": address, "chain": chain}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, config in enumerate(test_configs, 1):
            logger.info(f"\n--- Тест {i}: {config['method']} {config['url']} ---")
            
            try:
                headers = {
                    "API-KEY": settings.metasleuth_address_label_key,
                    "Content-Type": "application/json"
                }
                
                if config["method"] == "POST":
                    async with session.post(config["url"], json=config["payload"], headers=headers) as response:
                        logger.info(f"Status: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ Success! Response: {data}")
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Error: {error_text}")
                else:
                    async with session.get(config["url"], params=config["params"], headers=headers) as response:
                        logger.info(f"Status: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ Success! Response: {data}")
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Error: {error_text}")
                            
            except Exception as e:
                logger.error(f"Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_address_label_endpoints())
