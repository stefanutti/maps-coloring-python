import logging.handlers
import sys
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging_stream_handler = logging.StreamHandler(sys.stdout)
logging_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
logger.addHandler(logging_stream_handler)

if logger.isEnabledFor(logging.DEBUG): logger.debug("aaa", time.sleep(10))
if logger.isEnabledFor(logging.DEBUG): logger.debug("bbb")
if logger.isEnabledFor(logging.INFO): logger.info("ccc")
