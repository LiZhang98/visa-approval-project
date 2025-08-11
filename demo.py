from visa_approval.logger import logging
from visa_approval.exception import USvisaException
import sys
logging.info("Logger initialized successfully.")

try:
    1 / 0
except Exception as e:
    raise USvisaException(e, sys)
