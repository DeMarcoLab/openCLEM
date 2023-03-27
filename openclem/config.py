

import os
import openclem


BASE_PATH = openclem.__path__[0]
LOG_PATH = os.path.join(BASE_PATH, "log")

os.makedirs(LOG_PATH, exist_ok=True)