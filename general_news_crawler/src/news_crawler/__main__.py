

from __future__ import annotations

import sys
import time
import logging

LOG =logging.getLogger(__name__)

if __name__ == "__main__":
    from .cli.application import main
    start = time.time()
    res = main()
    end = time.time() 
    LOG.info("Execution time: ",end - start) 
    sys.exit(res)