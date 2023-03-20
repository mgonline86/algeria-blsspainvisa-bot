import logging

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('logs.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('[%(asctime)s](%(levelname)s): %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Add formatter to handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)