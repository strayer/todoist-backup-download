import logging
import os
import sys
from logging.handlers import SysLogHandler

DEBUG = True
TODOIST_TOKEN = ""
BACKUP_PATH = os.path.join(os.path.dirname(__file__), "backups")

SYSLOG_ENABLED = False
if sys.platform == "linux":
    SYSLOG_ADDRESS = "/dev/log"
else:
    SYSLOG_ADDRESS = None

try:
    from settings_local import *
except ImportError:
    print(
        "ERROR: Please configure your settings in settings_local.py",
        file=sys.stderr
    )
    sys.exit(1)


logging_handlers = None
logging_format = "%(levelname)s: %(message)s"
if SYSLOG_ENABLED and SYSLOG_ADDRESS:
    logging_handlers = [
        SysLogHandler(address=SYSLOG_ADDRESS)
    ]
    logging_format = "todoist-backup-download: %s" % logging_format

logging.basicConfig(
    format=logging_format,
    level=logging.INFO if not DEBUG else logging.DEBUG,
    handlers=logging_handlers
)
