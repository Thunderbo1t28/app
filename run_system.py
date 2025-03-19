#!/usr/bin/env python
import os
import sys
import time
import signal
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('private/system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SystemRunner')

class SystemRunner:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        signal.signal(signal.SIGINT, self.handle_sigterm)

    def handle_sigterm(self, signum, frame):
        logger.info("Received shutdown signal")
        self.running = False

    def run(self):
        logger.info("Starting system...")
        
        try:
            while self.running:
                # Здесь будет основная логика работы системы
                logger.info(f"System running at {datetime.now()}")
                time.sleep(60)  # Проверяем каждую минуту
                
        except Exception as e:
            logger.error(f"System error: {str(e)}")
            return 1
        finally:
            logger.info("System shutdown")
        
        return 0

if __name__ == "__main__":
    runner = SystemRunner()
    sys.exit(runner.run()) 