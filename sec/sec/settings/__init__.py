import logging
from .base import *

try:
    from .dev import *

except ImportError:
    logging.info("Development settings not found.")
    try:
        from .prod import *
    except ImportError:
        logging.error("Production settings not found.")
