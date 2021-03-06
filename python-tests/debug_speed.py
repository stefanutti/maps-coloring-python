import logging.handlers
import time

# Set logging facilities
logger = logging.getLogger()
logger.setLevel(logging.INFO)

print("Time", time.ctime())
for i in range(1000000):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN 1: restore an F2 (multiple edge)" + str(i) + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b")
print("Time", time.ctime())

print("--------------------")

logger.setLevel(logging.INFO)
print("Time", time.ctime())
for i in range(6000000):
    logger.debug("BEGIN 1: restore an F2 (multiple edge)" + str(i) + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b" + "b")
print("Time", time.ctime())

print("--------------------")

print("Time", time.ctime())
for i in range(60000000):
    if logger.isEnabledFor(logging.DEBUG): logger.debug("BEGIN 2: restore an F2 (multiple edge): %s, %s, %s, %s", i, "a", "bb", "ccc")
print("Time", time.ctime())

print("--------------------")

logger.setLevel(logging.INFO)
print("Time", time.ctime())
for i in range(10000000):
    logger.debug("BEGIN 2: restore an F2 (multiple edge): %s, %s, %s, %s", i, "a", "bb", "ccc")
print("Time", time.ctime())
