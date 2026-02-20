"""
Test script to generate ERROR and CRITICAL logs for testing
"""
import logging
import sys
import os
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), 'logs', 'assistant.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('test_logs')

# Generate test logs
logger.info('Starting test log generation...')

# Generate some INFO logs
for i in range(5):
    logger.info(f'Test info log {i+1}')

# Generate some WARNING logs
for i in range(3):
    logger.warning(f'Test warning log {i+1}')

# Generate some ERROR logs
for i in range(4):
    logger.error(f'Test error log {i+1}: Simulated error condition')

# Generate some CRITICAL logs
for i in range(2):
    logger.critical(f'Test critical log {i+1}: System critical failure')

logger.info('Test log generation completed')
print('Test logs generated successfully!')
