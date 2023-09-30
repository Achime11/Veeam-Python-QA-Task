# Python script that synchronizes two folders one-way: source to the replica.

# imports
import logging


# Configure the logger
logger = logging.getLogger("Sync One-Way")
logger.setLevel(logging.DEBUG)

# Create a file handler to log to a file
file_handler = logging.FileHandler('example.log')
file_handler.setLevel(logging.INFO)

# Create a console handler to log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set the formatter
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Test log types
logger.debug('Debug test message')
logger.info('Info test message')
logger.error('Error test message')
